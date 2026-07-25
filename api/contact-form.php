<?php
declare(strict_types=1);

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

const RECIPIENTS = [
    'rebbert@jrhconstructions.com',
    'Rachelbrum@yahoo.com',
    'Info@axelseo.com',
];

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

if ($name === '' || $email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(422);
    echo json_encode(['success' => false, 'message' => 'Please fill in your name and a valid email address.']);
    exit;
}

$subject = 'JRH Constructions — New contact form submission';
if ($formName !== '') {
    $subject .= ' (' . $formName . ')';
}

$bodyLines = [
    'New submission from jrhconstructions.com',
    '',
    'Name: ' . $name,
    'Email: ' . $email,
    'Phone: ' . ($phone !== '' ? $phone : '—'),
    'City, State: ' . ($cityState !== '' ? $cityState : '—'),
    'Form: ' . ($formName !== '' ? $formName : '—'),
    'Page: ' . ($pageTitle !== '' ? $pageTitle : '—'),
    'URL: ' . ($pageUrl !== '' ? $pageUrl : '—'),
    '',
    'Message:',
    $message !== '' ? $message : '—',
];

$body = implode("\n", $bodyLines);
$headers = [
    'From: JRH Constructions <noreply@jrhconstructions.com>',
    'Reply-To: ' . $name . ' <' . $email . '>',
    'Content-Type: text/plain; charset=UTF-8',
];

$sent = mail(implode(', ', RECIPIENTS), $subject, $body, implode("\r\n", $headers));

if (!$sent) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'We could not send your message. Please call us or try again later.']);
    exit;
}

echo json_encode([
    'success' => true,
    'message' => 'Thank you! Your message has been sent successfully.',
]);
