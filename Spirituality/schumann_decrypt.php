<?php
// schumann_dashboard_stylish.php

/**
 * Fetches and saves an image from a remote URL.
 */
function fetchImage() {
    $url = "https://images.weserv.nl/?url=sosrff.tsu.ru/new/shm.jpg";
    $outputPath = __DIR__ . '/temp/schumann_image.jpg';

    if (!is_dir(__DIR__ . '/temp')) {
        mkdir(__DIR__ . '/temp', 0777, true);
    }

    // Fetch and save the image
    $imageData = file_get_contents($url);
    if ($imageData === false) {
        throw new Exception("Failed to fetch the image from URL.");
    }
    file_put_contents($outputPath, $imageData);

    return $outputPath;
}

/**
 * Analyze image colors and compute proportions.
 */
function analyzeImageColors($imagePath) {
    $image = imagecreatefromjpeg($imagePath);
    if (!$image) {
        throw new Exception("Failed to load the image.");
    }

    $width = imagesx($image);
    $height = imagesy($image);

    // Define color ranges
    $colorRanges = [
        "Homeostasis/Calm (Blue)" => [[0, 0, 128], [50, 50, 255]],
        "Density/Blockages (Red)" => [[128, 0, 0], [255, 50, 50]],
        "3D Purge Energies (Green)" => [[0, 128, 0], [50, 255, 50]],
        "5D Light Coding (White)" => [[200, 200, 200], [255, 255, 255]],
    ];

    // Count pixel colors
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

    // Calculate proportions
    $totalPixels = $width * $height;
    $proportions = [];
    foreach ($colorCounts as $label => $count) {
        $proportions[$label] = ($count / $totalPixels) * 100;
    }

    imagedestroy($image);
    return $proportions;
}

/**
 * Render a stylish dashboard.
 */
function renderDashboard($imagePath, $colorProportions) {
    $descriptions = [
        "Homeostasis/Calm (Blue)" => "Promotes emotional stability, stress relief, and physical grounding.",
        "Density/Blockages (Red)" => "Indicates resistance or anxiety. May be linked to emotional or energetic blockages.",
        "3D Purge Energies (Green)" => "Represents detoxification and healing. Encourages renewal.",
        "5D Light Coding (White)" => "Symbolizes clarity, spiritual awakening, and higher consciousness.",
    ];

    echo "<!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Schumann Resonance Stylish Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                color: #333;
                margin: 0;
                padding: 20px;
                line-height: 1.6;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #3498db;
                text-align: center;
                margin-bottom: 20px;
            }
            img {
                display: block;
                max-width: 100%;
                margin: 20px auto;
                border: 3px solid #ddd;
                border-radius: 5px;
            }
            .chart {
                margin-top: 20px;
            }
            .chart-bar {
                background: #3498db;
                height: 20px;
                margin: 10px 0;
                border-radius: 3px;
            }
            .chart-label {
                margin-top: 5px;
                font-weight: bold;
                text-align: center;
            }
            .description {
                background: #f9f9f9;
                padding: 15px;
                margin-top: 10px;
                border-radius: 5px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
        </style>
    </head>
    <body>
        <div class='container'>
            <h1>Schumann Resonance Dashboard</h1>
            <img src='temp/schumann_image.jpg' alt='Schumann Resonance Image'>
            <h2>Current Readings</h2>";

    foreach ($colorProportions as $label => $value) {
        $description = $descriptions[$label];
        echo "
            <div class='chart'>
                <div class='chart-bar' style='width: {$value}%;'></div>
                <div class='chart-label'>{$label}: " . round($value, 2) . "%</div>
                <div class='description'>{$description}</div>
            </div>";
    }

    echo "
        </div>
    </body>
    </html>";
}

/**
 * Main execution flow.
 */
try {
    $imagePath = fetchImage();
    $colorProportions = analyzeImageColors($imagePath);
    renderDashboard($imagePath, $colorProportions);
} catch (Exception $e) {
    echo "Error: " . $e->getMessage();
}
