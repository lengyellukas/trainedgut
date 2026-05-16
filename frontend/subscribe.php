<?php
/**
 * TrainedGut.com - Email Subscription Handler
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
    // Already subscribed - return success silently (don't expose data)
    echo json_encode(['success' => true, 'message' => 'You\'re already subscribed - check your inbox for the discount code.']);
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
$subject = SITE_NAME . ' - New newsletter subscriber';
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
$confirm_subject = "Your 10% off " . SITE_NAME . " - welcome";
$confirm_body    = "Hi,\n\n"
                 . "Thanks for signing up. Here's your 10% discount code for your first personalised gut training plan:\n\n"
                 . "    GUT10\n\n"
                 . "Apply it at checkout on trainedgut.store. Works on any plan length and any race type.\n\n"
                 . "What you signed up for: roughly one email per month with research summaries on carbohydrate absorption and gut adaptation, plus updates as the protocol is refined with our sports nutritionist. No spam, ever.\n\n"
                 . "If gut training is new to you, the 30-second version: during efforts over 2 hours, carbohydrate availability - not fitness - becomes the limiter on performance. Your gut's carb transporters (SGLT1, GLUT5) adapt to repeated high-carb exposure. TrainedGut is a progressive 8-20 week protocol that trains them, week by week, around your specific race.\n\n"
                 . "Ready when you are: https://trainedgut.store\n\n"
                 . "- The TrainedGut team\n"
                 . "trainedgut.com";

$confirm_headers  = "From: " . SITE_NAME . " <" . FROM_EMAIL . ">\r\n";
$confirm_headers .= "Reply-To: " . FROM_EMAIL . "\r\n";
$confirm_headers .= "X-Mailer: PHP/" . phpversion();

mail($email, $confirm_subject, $confirm_body, $confirm_headers);

// Success
echo json_encode([
    'success' => true,
    'message' => 'Welcome! Check your inbox for your 10% discount code.'
]);
