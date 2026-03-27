<?php
// ==========================================
// api.php - API REST pour CYBER-PATH (V1.1)
// ==========================================
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$host = '127.0.0.1';
$db   = 'cyber_path';
$user = 'admin';
$pass = 'admin';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=utf8mb4", $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
    ]);
} catch (\PDOException $e) {
    echo json_encode(['error' => 'Erreur DB: ' . $e->getMessage()]);
    exit;
}

// Récupération des 50 dernières trajectoires
$sql = "SELECT HEX(t.id_emp) as id_hex, t.timestamp, t.vector_data 
        FROM trajectories t 
        ORDER BY t.timestamp DESC LIMIT 50";
$stmt = $pdo->query($sql);
$logs = $stmt->fetchAll();

$result = [];
foreach ($logs as $log) {
    $vector = unpack("f5", $log['vector_data']); 
    
    // Vérification de sécurité pour s'assurer que unpack a fonctionné
    if (!$vector || count($vector) < 5) {
        continue; 
    }

    $dims = [
        round($vector[1], 2), 
        round($vector[2], 2), 
        round($vector[3], 2), 
        round($vector[4], 2), 
        round($vector[5], 2)
    ];
    
    // Calcul d'un score de risque (moyenne)
    $risk_score = array_sum($dims) / 5;
    
    // Détermination de la sévérité
    $severity = 'LOW';
    if ($risk_score >= 0.7) $severity = 'CRITICAL';
    elseif ($risk_score >= 0.5) $severity = 'HIGH';
    elseif ($risk_score >= 0.3) $severity = 'MEDIUM';

    // Simulation de la corrélation MITRE (test visuel)
    // Si le vecteur est très proche de notre T1059 expert [0.8, 0.9, 0.7, 1.0, 0.6]
    $mitre_match = null;
    if ($dims[0] >= 0.7 && $dims[1] >= 0.8 && $dims[3] >= 0.9) {
        $mitre_match = [
            'tid' => 'T1059',
            'name' => 'Command Interpreter',
            'desc' => 'Adversaries may abuse... to execute commands, scripts, or binaries.'
        ];
    }

    $result[] = [
        'id' => uniqid(), // ID unique pour le DOM
        'timestamp' => $log['timestamp'],
        'id_hex' => $log['id_hex'],
        'dimensions' => $dims,
        'risk_score' => round($risk_score, 2),
        'severity' => $severity,
        'mitre' => $mitre_match
    ];
}

// Tri par score de risque décroissant
usort($result, function($a, $b) {
    return $b['risk_score'] <=> $a['risk_score'];
});

echo json_encode($result);
?>