<?php
/**
 * TrainedGut.com — Email Subscription Handler
 * 
 * SETUP INSTRUCTIONS (do this once in WebSupport WebAdmin):
 * 1. Go to WebAdmin → Databases → Create new database
 *    - Database name: trainedgut_db (or any name you choose)
 *    - Note down: host, database name, username, password
 * 2. Go to WebAdmin → phpMyAdmin → select your database → SQL tab
 *    - Run the CREATE TABLE query from setup.sql
 * 3. Fill in your credentials in the CONFIG section below
 * 4. Upload this file alongside index.html via FTP
 */

// ── CONFIG ──────────────────────────────────────────────────────────────────
require_once __DIR__ . '/config.php';
// ────────────────────────────────────────────────────────────────────────────

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: https://www.trainedgut.com');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// Only accept POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    exit;
}

// Get and sanitise input
$raw   = file_get_contents('php://input');
$data  = json_decode($raw, true);
$email = isset($data['email']) ? trim(strtolower($data['email'])) : '';

// Also support plain form POST
if (empty($email) && isset($_POST['email'])) {
    $email = trim(strtolower($_POST['email']));
}

// Validate email
if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Please enter a valid email address.']);
    exit;
}

// Connect to database
try {
    $pdo = new PDO(
        "pgsql:host=" . DB_HOST . ";dbname=" . DB_NAME,
        DB_USER,
        DB_PASS,
        [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ]
    );
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Database connection failed. Please try again.']);
    exit;
}

// Check for duplicate
$stmt = $pdo->prepare("SELECT id FROM subscribers WHERE email = ?");
$stmt->execute([$email]);

if ($stmt->fetch()) {
    // Already subscribed — return success silently (don't expose data)
    echo json_encode(['success' => true, 'message' => 'You\'re already on the list — we\'ll be in touch before launch.']);
    exit;
}

// Insert new subscriber
try {
    $stmt = $pdo->prepare("
        INSERT INTO subscribers (email, source, ip_address, created_at)
        VALUES (?, ?, ?, NOW())
    ");
    $source     = isset($data['source']) ? substr($data['source'], 0, 50) : 'landing_page';
    $ip_address = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? '';

    $stmt->execute([$email, $source, $ip_address]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Could not save your email. Please try again.']);
    exit;
}

// Send notification email to you
$subject = SITE_NAME . ' — New Early Access Signup';
$body    = "New signup on TrainedGut.com\n\n"
         . "Email: {$email}\n"
         . "Time:  " . date('Y-m-d H:i:s') . "\n"
         . "IP:    {$ip_address}\n\n"
         . "Log in to WebAdmin → phpMyAdmin to view all subscribers.";

$headers  = "From: " . FROM_EMAIL . "\r\n";
$headers .= "Reply-To: " . FROM_EMAIL . "\r\n";
$headers .= "X-Mailer: PHP/" . phpversion();

mail(NOTIFY_EMAIL, $subject, $body, $headers);

// Send confirmation email to subscriber
$confirm_subject = "You're on the list — " . SITE_NAME;
$confirm_body    = "Hi,\n\n"
                 . "You're registered for early access to TrainedGut - the world's first\n"
                 . "personalised gut-training program for endurance athletes.\n\n"
                 . "We'll be in touch before launch with exclusive early pricing.\n\n"
                 . "In the meantime, if you have any questions, reply to this email.\n\n"
                 . "Train your gut, fuel your race\n"
                 . "The TrainedGut Team\n"
                 . "trainedgut.com";

$confirm_headers  = "From: " . SITE_NAME . " <" . FROM_EMAIL . ">\r\n";
$confirm_headers .= "Reply-To: " . FROM_EMAIL . "\r\n";
$confirm_headers .= "X-Mailer: PHP/" . phpversion();

mail($email, $confirm_subject, $confirm_body, $confirm_headers);

// Success
echo json_encode([
    'success' => true,
    'message' => 'You\'re on the list. Watch your inbox — we launch soon.'
]);
