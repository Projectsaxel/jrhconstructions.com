<?php

/**
 * SMTP configuration template for the JRH Constructions contact form.
 *
 * HOW TO ACTIVATE AUTHENTICATED EMAIL:
 *   1. Copy this file and rename the copy to  config.local.php
 *      (same /api folder). config.local.php is git-ignored and blocked
 *      from the web, so credentials never leak.
 *   2. Fill in the Microsoft 365 app password generated for the mailbox
 *      below (ask Rebbert to create one).
 *   3. Upload config.local.php to /api on the server.
 *
 * Until config.local.php exists, the form still works: every lead is saved
 * to /api/leads/ and the script attempts local mail() as a last resort.
 */

return [
    'smtp' => [
        'enabled'   => true,
        'host'      => 'smtp.office365.com',
        'port'      => 587,
        'secure'    => 'tls', // 'tls' for port 587, 'ssl' for port 465
        'username'  => 'rebbert@jrhconstructions.com', // the M365 mailbox that signs in
        'password'  => 'PASTE_M365_APP_PASSWORD_HERE',
        'from'      => 'rebbert@jrhconstructions.com', // must be the same mailbox (or an allowed alias)
        'from_name' => 'JRH Constructions Website',
    ],
];
