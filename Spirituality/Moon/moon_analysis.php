<?php
// moon_analyse.php

// Check if a city is provided via GET, default to "campbellton"
$city = isset($_GET['city']) ? htmlspecialchars($_GET['city']) : "campbellton";
$url = "https://www.timeanddate.com/moon/phases/canada/{$city}";

// Fetch the content of the page
$html = file_get_contents($url);

// Check if the content was fetched successfully
if ($html === false) {
    die("Failed to fetch data from the URL.");
}

// Load the HTML into a DOM parser
$dom = new DOMDocument();
libxml_use_internal_errors(true); // Suppress warnings for invalid HTML
$dom->loadHTML($html);
libxml_clear_errors();

// Create an XPath object to query the DOM
$xpath = new DOMXPath($dom);

// Extract current moon info
$currentMoonPhase = $xpath->evaluate('string(//div[@id="qlook"]//a[@title]/text())');
$currentIllumination = $xpath->evaluate('string(//div[@id="qlook"]//span[@id="cur-moon-percent"]/text())');

// Extract the upcoming moon phases
$phases = [];
$phaseNodes = $xpath->query('//div[contains(@class, "moon-phases-card")]');

foreach ($phaseNodes as $node) {
    $title = trim($xpath->evaluate('string(.//h3/a/text())', $node));
    $date = trim($xpath->evaluate('string(.//div[@class="moon-phases-card__date"]/text())', $node));
    $time = trim($xpath->evaluate('string(.//div[@class="moon-phases-card__time"]/text())', $node));
    
    // Only add valid phases with both date and time
    if (!empty($title) && !empty($date) && !empty($time)) {
        $phases[] = [
            'title' => $title,
            'date' => $date,
            'time' => $time,
        ];
    }
}

// Archetype descriptions (loaded from PDFs)
$archetypes = [
    "Witches" => [
        "Full Moon" => "During the Full Moon, Witches experience heightened emotional intensity and creativity. Grounding routines and mindfulness are essential to balance this energy.",
        "New Moon" => "The New Moon invites introspection for Witches. A great time for journaling, setting intentions, and emotional healing.",
        "Third Quarter" => "This phase encourages Witches to let go of emotional baggage and practice mindfulness.",
        "First Quarter" => "A phase for action and creative expression. Witches thrive by channeling energy into artistic or spiritual pursuits."
    ],
    "Mystics" => [
        "Full Moon" => "The Full Moon amplifies visionary thinking in Mystics, but grounding techniques are needed to avoid overstimulation.",
        "New Moon" => "An introspective time for Mystics, ideal for deep meditative practices and goal-setting.",
        "Third Quarter" => "Mystics can focus on abstract problem-solving and reviewing past ideas to refine them.",
        "First Quarter" => "This is a time for action-oriented thinking and structured philosophical exploration for Mystics."
    ],
    "Androids" => [
        "Full Moon" => "Sensory sensitivity may peak during the Full Moon for Androids. Calming routines and mindfulness are beneficial.",
        "New Moon" => "The New Moon is a perfect time for Androids to engage in structured planning and goal-setting.",
        "Third Quarter" => "Androids can declutter their thoughts and optimize routines during this phase.",
        "First Quarter" => "Androids excel in detail-oriented tasks and logical planning during this phase."
    ]
];

// City dropdown options
$cities = [
    "campbellton" => "Campbellton",
    "toronto" => "Toronto",
    "vancouver" => "Vancouver",
    "montreal" => "Montreal",
    "calgary" => "Calgary"
];

// Display the extracted data
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Moon Phase Analysis</title>
    <link rel="stylesheet" href="moonstyle.css">
</head>
<body>
    <div class="moon-info">
        <h1>Moon Phase Information</h1>
        
        <form method="GET" class="city-select">
            <label for="city">Select City:</label>
            <select name="city" id="city" onchange="this.form.submit()">
                <?php foreach ($cities as $key => $label): ?>
                    <option value="<?php echo $key; ?>" <?php echo $key === $city ? 'selected' : ''; ?>>
                        <?php echo $label; ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </form>
        
        <h2>Current Moon</h2>
        <p>Phase: <strong><?php echo htmlspecialchars($currentMoonPhase); ?></strong></p>
        <p>Illumination: <strong><?php echo htmlspecialchars($currentIllumination); ?></strong></p>
        
        <h2>Upcoming Phases</h2>
        <ul class="moon-phases">
            <?php foreach ($phases as $phase): ?>
                <li>
                    <h3><?php echo htmlspecialchars($phase['title']); ?></h3>
                    <p>Date: <?php echo htmlspecialchars($phase['date']); ?></p>
                    <p>Time: <?php echo htmlspecialchars($phase['time']); ?></p>
                    <div class="archetype-details">
                        <h4>Archetypes</h4>
                        <?php foreach ($archetypes as $archetype => $descriptions): ?>
                            <p><strong><?php echo $archetype; ?>:</strong> <?php echo $descriptions[$phase['title']] ?? 'N/A'; ?></p>
                        <?php endforeach; ?>
                    </div>
                </li>
            <?php endforeach; ?>
        </ul>
    </div>
</body>
</html>
