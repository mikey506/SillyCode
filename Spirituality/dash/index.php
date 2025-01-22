<?php
// moon_schumann_dashboard.php

/**
 * Fetches and saves the Schumann Resonance image.
 */
function fetchSchumannImage() {
    $url = "https://images.weserv.nl/?url=sosrff.tsu.ru/new/shm.jpg";
    $outputPath = __DIR__ . '/temp/schumann_image.jpg';

    if (!is_dir(__DIR__ . '/temp')) {
        mkdir(__DIR__ . '/temp', 0777, true);
    }

    $imageData = file_get_contents($url);
    if ($imageData === false) {
        throw new Exception("Failed to fetch the Schumann Resonance image.");
    }
    file_put_contents($outputPath, $imageData);

    return $outputPath;
}

/**
 * Analyzes Schumann Resonance image for color proportions.
 */
function analyzeSchumannColors($imagePath) {
    $image = imagecreatefromjpeg($imagePath);
    if (!$image) {
        throw new Exception("Failed to load the Schumann Resonance image.");
    }

    $width = imagesx($image);
    $height = imagesy($image);

    $colorRanges = [
        "Homeostasis/Calm (Blue)" => [[0, 0, 128], [50, 50, 255]],
        "Density/Blockages (Red)" => [[128, 0, 0], [255, 50, 50]],
        "3D Purge Energies (Green)" => [[0, 128, 0], [50, 255, 50]],
        "5D Light Coding (White)" => [[200, 200, 200], [255, 255, 255]],
    ];

    $colorCounts = array_fill_keys(array_keys($colorRanges), 0);
    for ($x = 0; $x < $width; $x++) {
        for ($y = 0; $y < $height; $y++) {
            $rgb = imagecolorat($image, $x, $y);
            $colors = imagecolorsforindex($image, $rgb);
            foreach ($colorRanges as $label => [$lower, $upper]) {
                if (
                    $colors['red'] >= $lower[0] && $colors['red'] <= $upper[0] &&
                    $colors['green'] >= $lower[1] && $colors['green'] <= $upper[1] &&
                    $colors['blue'] >= $lower[2] && $colors['blue'] <= $upper[2]
                ) {
                    $colorCounts[$label]++;
                }
            }
        }
    }

    $totalPixels = $width * $height;
    $proportions = [];
    foreach ($colorCounts as $label => $count) {
        $proportions[$label] = ($count / $totalPixels) * 100;
    }

    imagedestroy($image);
    return $proportions;
}

/**
 * Fetches lunar data for a city.
 */
function fetchLunarData($city) {
    $url = "https://www.timeanddate.com/moon/phases/canada/{$city}";
    $html = file_get_contents($url);

    if ($html === false) {
        throw new Exception("Failed to fetch lunar data.");
    }

    $dom = new DOMDocument();
    libxml_use_internal_errors(true);
    $dom->loadHTML($html);
    libxml_clear_errors();

    $xpath = new DOMXPath($dom);

    $currentMoonPhase = $xpath->evaluate('string(//div[@id="qlook"]//a[@title]/text())');
    $currentIllumination = $xpath->evaluate('string(//div[@id="qlook"]//span[@id="cur-moon-percent"]/text())');
    $moonImage = $xpath->evaluate('string(//div[@id="qlook"]//img/@src)');

    $phases = [];
    $phaseNodes = $xpath->query('//div[contains(@class, "moon-phases-card")]');
    foreach ($phaseNodes as $node) {
        $title = trim($xpath->evaluate('string(.//h3/a/text())', $node));
        $date = trim($xpath->evaluate('string(.//div[@class="moon-phases-card__date"]/text())', $node));
        $time = trim($xpath->evaluate('string(.//div[@class="moon-phases-card__time"]/text())', $node));
        $image = trim($xpath->evaluate('string(.//img/@src)', $node));
        if (!empty($title) && !empty($date) && !empty($time)) {
            $phases[] = compact('title', 'date', 'time', 'image');
        }
    }

    return [
        'currentPhase' => $currentMoonPhase,
        'illumination' => $currentIllumination,
        'moonImage' => "https://www.timeanddate.com{$moonImage}",
        'phases' => $phases,
    ];
}

/**
 * Renders the dashboard.
 */
function renderDashboard($lunarData, $schumannProportions) {
    $cities = [
        "campbellton" => "Campbellton",
        "toronto" => "Toronto",
        "vancouver" => "Vancouver",
        "montreal" => "Montreal",
        "calgary" => "Calgary",
    ];

    $currentPhase = htmlspecialchars($lunarData['currentPhase']);
    $illumination = htmlspecialchars($lunarData['illumination']);
    $moonImage = htmlspecialchars($lunarData['moonImage']);
    $phases = $lunarData['phases'];

    echo "<!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Moon & Schumann Dashboard</title>
        <link rel='stylesheet' href='dashboard.css'>
    </head>
    <body>
        <div class='container'>
            <h1>Moon & Schumann Dashboard</h1>
            <form method='GET'>
                <label for='city'>Select City: </label>
                <select name='city' id='city' onchange='this.form.submit()'>";
    foreach ($cities as $key => $label) {
        $selected = $key === ($_GET['city'] ?? 'campbellton') ? 'selected' : '';
        echo "<option value='{$key}' {$selected}>{$label}</option>";
    }
    echo "      </select>
            </form>

            <div class='section'>
                <h2>Moon Phases</h2>
                <div class='current-moon'>
                    <img src='{$moonImage}' alt='Current Moon Phase'>
                    <p><strong>Current Phase:</strong> {$currentPhase}</p>
                    <p><strong>Illumination:</strong> {$illumination}</p>
                </div>
                <div class='upcoming-phases moon-phases'>";
    foreach ($phases as $phase) {
        echo "
                    <div class='moon-phase'>
                        <img src='https://www.timeanddate.com{$phase['image']}' alt='{$phase['title']}'>
                        <h3>{$phase['title']}</h3>
                        <p><strong>Date:</strong> {$phase['date']}</p>
                        <p><strong>Time:</strong> {$phase['time']}</p>
                    </div>";
    }
    echo "      </div>
            </div>

            <div class='section'>
                <h2>Schumann Resonance Analysis</h2>
                <img src='temp/schumann_image.jpg' alt='Schumann Resonance'>
                <table>
                    <tr><th>Category</th><th>Proportion (%)</th></tr>";
    foreach ($schumannProportions as $label => $value) {
        echo "<tr><td>{$label}</td><td>" . round($value, 2) . "%</td></tr>";
    }
    echo "      </table>
            </div>
        </div>
    </body>
    </html>";
}

// Main execution
try {
    $city = $_GET['city'] ?? 'campbellton';
    $schumannImage = fetchSchumannImage();
    $schumannProportions = analyzeSchumannColors($schumannImage);
    $lunarData = fetchLunarData($city);
    renderDashboard($lunarData, $schumannProportions);
} catch (Exception $e) {
    echo "Error: " . $e->getMessage();
}
?>
