<?php

declare(strict_types=1);

/**
 * JRH Constructions - contact form handler.
 *
 * Design goals (after the 2026-07 audit that found ~1 year of silently lost leads):
 *  1. NEVER lose a lead again. Every valid submission is written to a protected
 *     file on the server FIRST, before any email is attempted. Even if email
 *     delivery fails, the lead is safely captured and can be read from
 *     /api/leads/ via the Hostinger File Manager.
 *  2. Deliver email through AUTHENTICATED SMTP (Microsoft 365) when configured,
 *     so mail passes the domain SPF (-all) / DKIM instead of being dropped.
 *     Local mail() is only a last-resort fallback and is NOT trusted.
 *  3. NEVER report success to the visitor unless the lead was actually captured.
 *     The old endpoint returned {"success":true} even when nothing was delivered.
 */

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    exit;
}

/* -------------------------------------------------------------------------
 * Recipients (confirmed by the client on 2026-07-25).
 * ---------------------------------------------------------------------- */
const RECIPIENTS = [
    'rebbert@jrhconstructions.com',
    'Rachelbrum@yahoo.com',
    'Info@axelseo.com',
];

// Default delivery method: FormSubmit (formsubmit.co). It relays mail through
// FormSubmit's own authenticated servers, so it is NOT affected by the domain's
// SPF -all rule that was silently dropping mail. No Microsoft password and no
// DNS change required for the form to work. Can be overridden in config.local.php
// (e.g. to switch to authenticated Microsoft 365 SMTP later).
const FORMSUBMIT_DEFAULT_ENABLED = true;

/* -------------------------------------------------------------------------
 * Optional SMTP configuration.
 * Copy config.example.php to config.local.php and fill in the credentials.
 * config.local.php is git-ignored and blocked from web access.
 * ---------------------------------------------------------------------- */
$config = [];
$configPath = __DIR__ . '/config.local.php';
if (is_file($configPath)) {
    $loaded = require $configPath;
    if (is_array($loaded)) {
        $config = $loaded;
    }
}

function read_field(string $key): string
{
    $value = $_POST[$key] ?? '';
    if (is_array($value)) {
        return '';
    }
    // Strip CR/LF so submitted values can never inject extra mail headers.
    return trim(str_replace(["\r", "\n"], ' ', (string) $value));
}

function read_multiline_field(string $key): string
{
    $value = $_POST[$key] ?? '';
    if (is_array($value)) {
        return '';
    }
    return trim(str_replace("\r\n", "\n", (string) $value));
}

$name = read_field('name');
$phone = read_field('phone');
$email = read_field('email');
$cityState = read_field('city_state');
$message = read_multiline_field('message');
$pageTitle = read_field('page_title');
$pageUrl = read_field('page_url');
$formName = read_field('form_name');

// Simple honeypot: if a hidden field named "website" is filled, treat as spam
// but still answer 200 so bots get no signal. Nothing is stored or emailed.
$honeypot = read_field('website');
if ($honeypot !== '') {
    echo json_encode(['success' => true, 'message' => 'Thank you! Your message has been sent successfully.']);
    exit;
}

if ($name === '' || $email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(422);
    echo json_encode(['success' => false, 'message' => 'Please fill in your name and a valid email address.']);
    exit;
}

$subject = 'JRH Constructions - New contact form submission';
if ($formName !== '') {
    $subject .= ' (' . $formName . ')';
}

$submittedAt = gmdate('Y-m-d H:i:s') . ' UTC';
$sourceIp = $_SERVER['REMOTE_ADDR'] ?? '';

$bodyLines = [
    'New submission from jrhconstructions.com',
    '',
    'Name: ' . $name,
    'Email: ' . $email,
    'Phone: ' . ($phone !== '' ? $phone : '-'),
    'City, State: ' . ($cityState !== '' ? $cityState : '-'),
    'Form: ' . ($formName !== '' ? $formName : '-'),
    'Page: ' . ($pageTitle !== '' ? $pageTitle : '-'),
    'URL: ' . ($pageUrl !== '' ? $pageUrl : '-'),
    'Submitted: ' . $submittedAt,
    '',
    'Message:',
    $message !== '' ? $message : '-',
];
$body = implode("\n", $bodyLines);

/* -------------------------------------------------------------------------
 * STEP 1 - Capture the lead to disk. This is the safety net.
 * ---------------------------------------------------------------------- */
$captured = capture_lead([
    'submitted_at' => $submittedAt,
    'name' => $name,
    'email' => $email,
    'phone' => $phone,
    'city_state' => $cityState,
    'message' => $message,
    'form_name' => $formName,
    'page_title' => $pageTitle,
    'page_url' => $pageUrl,
    'ip' => $sourceIp,
]);

/* -------------------------------------------------------------------------
 * STEP 2 - Try to email the lead. Preferred: authenticated SMTP. If SMTP is
 * not configured yet, fall back to local mail() but do NOT trust it.
 * ---------------------------------------------------------------------- */
$emailSent = false;
$emailError = '';

$fs = $config['formsubmit'] ?? [];
$fsEnabled = $fs['enabled'] ?? FORMSUBMIT_DEFAULT_ENABLED;
$smtp = $config['smtp'] ?? [];

if ($fsEnabled) {
    // Preferred: relay through FormSubmit (authenticated third-party sender).
    [$emailSent, $emailError] = send_via_formsubmit($fs, $name, $email, $subject, $body, $pageUrl);
} elseif (!empty($smtp['enabled']) && !empty($smtp['host']) && !empty($smtp['username']) && !empty($smtp['password'])) {
    // Alternative: authenticated Microsoft 365 SMTP.
    [$emailSent, $emailError] = send_via_smtp($smtp, $name, $email, $subject, $body);
} else {
    // Last resort only. Likely to be dropped by SPF -all.
    $headers = [
        'From: JRH Constructions <noreply@jrhconstructions.com>',
        'Reply-To: ' . $name . ' <' . $email . '>',
        'Content-Type: text/plain; charset=UTF-8',
    ];
    $emailSent = @mail(implode(', ', RECIPIENTS), $subject, $body, implode("\r\n", $headers));
    if (!$emailSent) {
        $emailError = 'local mail() returned false';
    }
}

log_outcome($captured, $emailSent, $emailError);

/* -------------------------------------------------------------------------
 * STEP 3 - Respond honestly. Success requires that we actually HAVE the lead
 * (captured to disk and/or emailed). We never fake success on total failure.
 * ---------------------------------------------------------------------- */
if ($captured || $emailSent) {
    echo json_encode([
        'success' => true,
        'message' => 'Thank you! Your message has been sent successfully. We will get back to you shortly.',
    ]);
    exit;
}

http_response_code(500);
echo json_encode([
    'success' => false,
    'message' => 'We could not send your message right now. Please call us or email rebbert@jrhconstructions.com.',
]);
exit;


/* ========================================================================
 * Helpers
 * ===================================================================== */

/**
 * Append the lead to a protected, human-readable log and a machine-readable
 * JSONL file. Returns true if at least the JSONL line was written.
 */
function capture_lead(array $lead): bool
{
    $dir = __DIR__ . '/leads';
    if (!is_dir($dir)) {
        @mkdir($dir, 0755, true);
    }
    // Keep the directory listing empty even if the server ignores .htaccess.
    if (!is_file($dir . '/index.html')) {
        @file_put_contents($dir . '/index.html', '');
    }

    $month = gmdate('Y-m');
    $jsonlOk = @file_put_contents(
        $dir . '/leads-' . $month . '.jsonl',
        json_encode($lead, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n",
        FILE_APPEND | LOCK_EX
    );

    // Friendly plain-text copy that opens cleanly in the File Manager.
    $txt = "==================================================\n"
        . 'Received: ' . $lead['submitted_at'] . "\n"
        . 'Name:     ' . $lead['name'] . "\n"
        . 'Email:    ' . $lead['email'] . "\n"
        . 'Phone:    ' . ($lead['phone'] !== '' ? $lead['phone'] : '-') . "\n"
        . 'City:     ' . ($lead['city_state'] !== '' ? $lead['city_state'] : '-') . "\n"
        . 'Form:     ' . ($lead['form_name'] !== '' ? $lead['form_name'] : '-') . "\n"
        . 'Page:     ' . ($lead['page_url'] !== '' ? $lead['page_url'] : '-') . "\n"
        . "Message:\n" . ($lead['message'] !== '' ? $lead['message'] : '-') . "\n\n";
    @file_put_contents($dir . '/leads-' . $month . '.txt', $txt, FILE_APPEND | LOCK_EX);

    return $jsonlOk !== false;
}

/**
 * Relay the lead through FormSubmit (formsubmit.co). FormSubmit requires an
 * Origin/Referer header from a real site, so we set them explicitly. The first
 * ever submission triggers a one-time "Activate Form" email to the primary
 * recipient; after it is clicked once, every submission is emailed.
 *
 * @return array{0:bool,1:string} [sent, statusOrError]
 */
function send_via_formsubmit(array $fs, string $name, string $replyTo, string $subject, string $body, string $pageUrl): array
{
    $primary = $fs['endpoint'] ?? RECIPIENTS[0];
    $ccValue = $fs['cc'] ?? array_slice(RECIPIENTS, 1);
    $cc = is_array($ccValue) ? implode(',', $ccValue) : (string) $ccValue;

    $url = 'https://formsubmit.co/ajax/' . rawurlencode($primary);

    $payload = [
        'name' => $name,
        'email' => $replyTo,
        'message' => $body,
        '_subject' => $subject,
        '_replyto' => $replyTo,
        '_template' => 'table',
        '_captcha' => 'false',
    ];
    if ($cc !== '') {
        $payload['_cc'] = $cc;
    }
    $json = json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

    $referer = $pageUrl !== '' ? $pageUrl : 'https://jrhconstructions.com/contact-us/';
    $headers = [
        'Content-Type: application/json',
        'Accept: application/json',
        'Origin: https://jrhconstructions.com',
        'Referer: ' . $referer,
    ];

    $respBody = false;
    $transportError = '';
    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $json,
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 15,
            CURLOPT_CONNECTTIMEOUT => 8,
        ]);
        $respBody = curl_exec($ch);
        if ($respBody === false) {
            $transportError = 'curl: ' . curl_error($ch);
        }
        curl_close($ch);
    } else {
        $ctx = stream_context_create(['http' => [
            'method' => 'POST',
            'header' => implode("\r\n", $headers),
            'content' => $json,
            'timeout' => 15,
            'ignore_errors' => true,
        ]]);
        $respBody = @file_get_contents($url, false, $ctx);
        if ($respBody === false) {
            $transportError = 'stream POST failed';
        }
    }

    if ($respBody !== false && $respBody !== '') {
        $data = json_decode((string) $respBody, true);
        $success = is_array($data) ? ($data['success'] ?? null) : null;
        if ($success === true || $success === 'true') {
            return [true, ''];
        }
        $msg = is_array($data) && isset($data['message'])
            ? (string) $data['message']
            : ('unexpected FormSubmit response: ' . substr((string) $respBody, 0, 200));
        return [false, 'FormSubmit: ' . $msg];
    }

    return [false, $transportError !== '' ? $transportError : 'no response from FormSubmit'];
}

/**
 * @return array{0:bool,1:string} [sent, errorMessage]
 */
function send_via_smtp(array $smtp, string $name, string $replyTo, string $subject, string $body): array
{
    $base = __DIR__ . '/lib/PHPMailer/';
    require_once $base . 'Exception.php';
    require_once $base . 'PHPMailer.php';
    require_once $base . 'SMTP.php';

    $mail = new \PHPMailer\PHPMailer\PHPMailer(true);
    try {
        $mail->isSMTP();
        $mail->Host = $smtp['host'];
        $mail->Port = (int) ($smtp['port'] ?? 587);
        $mail->SMTPAuth = true;
        $mail->Username = $smtp['username'];
        $mail->Password = $smtp['password'];
        $secure = strtolower((string) ($smtp['secure'] ?? 'tls'));
        $mail->SMTPSecure = $secure === 'ssl'
            ? \PHPMailer\PHPMailer\PHPMailer::ENCRYPTION_SMTPS
            : \PHPMailer\PHPMailer\PHPMailer::ENCRYPTION_STARTTLS;

        $fromAddr = $smtp['from'] ?? $smtp['username'];
        $fromName = $smtp['from_name'] ?? 'JRH Constructions Website';
        $mail->setFrom($fromAddr, $fromName);
        foreach (RECIPIENTS as $rcpt) {
            $mail->addAddress($rcpt);
        }
        $mail->addReplyTo($replyTo, $name);

        $mail->Subject = $subject;
        $mail->Body = $body;
        $mail->CharSet = 'UTF-8';

        $mail->send();
        return [true, ''];
    } catch (\Throwable $e) {
        return [false, $mail->ErrorInfo ?: $e->getMessage()];
    }
}

function log_outcome(bool $captured, bool $emailSent, string $emailError): void
{
    $dir = __DIR__ . '/leads';
    $line = gmdate('Y-m-d H:i:s') . ' UTC | captured=' . ($captured ? 'yes' : 'NO')
        . ' | email=' . ($emailSent ? 'sent' : 'FAILED')
        . ($emailError !== '' ? ' | error=' . str_replace(["\r", "\n"], ' ', $emailError) : '')
        . "\n";
    @file_put_contents($dir . '/delivery.log', $line, FILE_APPEND | LOCK_EX);
}
