<?php

/**
 * Optional configuration for the JRH Constructions contact form.
 *
 * YOU DO NOT NEED THIS FILE FOR THE FORM TO WORK.
 * By default the form delivers through FormSubmit (formsubmit.co), which needs
 * no password and no DNS change. Just deploy and do the one-time activation
 * click (see the deploy guide).
 *
 * Create api/config.local.php (a copy of this file) ONLY if you want to:
 *   - change the FormSubmit recipients, OR
 *   - switch delivery to authenticated Microsoft 365 SMTP instead of FormSubmit.
 *
 * config.local.php is git-ignored and blocked from web access.
 */

return [

    // ---- Option A: FormSubmit (default, recommended) --------------------
    'formsubmit' => [
        'enabled'  => true,
        // Primary recipient. This is the address that receives the one-time
        // "Activate Form" email. Must be a mailbox that can receive mail.
        'endpoint' => 'rebbert@jrhconstructions.com',
        // Everyone else gets a copy (comma list or array).
        'cc'       => ['Rachelbrum@yahoo.com', 'Info@axelseo.com'],
    ],

    // ---- Option B: Microsoft 365 SMTP (only if FormSubmit is disabled) ---
    // To use this instead, set formsubmit.enabled = false above and fill this in
    // with an app password generated for the mailbox.
    'smtp' => [
        'enabled'   => false,
        'host'      => 'smtp.office365.com',
        'port'      => 587,
        'secure'    => 'tls',
        'username'  => 'rebbert@jrhconstructions.com',
        'password'  => 'PASTE_M365_APP_PASSWORD_HERE',
        'from'      => 'rebbert@jrhconstructions.com',
        'from_name' => 'JRH Constructions Website',
    ],
];
