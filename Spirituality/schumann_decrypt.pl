#!/usr/bin/perl
use strict;
use warnings;
use OpenCV::Simple;
use GD::Graph::bars;
use POSIX qw(strftime);
use Tk;

# Define color ranges for decoding
my %color_ranges = (
    "Calm"    => [[0, 0, 128], [50, 50, 255]],     # Blue
    "Blockages" => [[128, 0, 0], [255, 50, 50]],   # Red
    "Purge"   => [[0, 128, 0], [50, 255, 50]],     # Green
    "Light"   => [[200, 200, 200], [255, 255, 255]] # White
);

# Load image function
sub load_image {
    my $file = shift || 'image.png'; # Replace with file dialog logic if needed
    my $img = OpenCV::Simple->imread($file, OpenCV::Simple::IMREAD_COLOR());
    die "Failed to load image $file\n" unless $img;
    return $img;
}

# Extract pixel counts
sub extract_pixel_counts {
    my ($img, $color_ranges) = @_;
    my %pixel_counts;
    for my $label (keys %$color_ranges) {
        my ($lower, $upper) = @{$color_ranges->{$label}};
        my $mask = OpenCV::Simple::inRange($img, OpenCV::Simple::Scalar(@$lower), OpenCV::Simple::Scalar(@$upper));
        $pixel_counts{$label} = OpenCV::Simple::countNonZero($mask);
    }
    return %pixel_counts;
}

# Display stats
sub show_stats {
    my ($img, $color_ranges) = @_;
    my %pixel_counts = extract_pixel_counts($img, $color_ranges);
    my $total_pixels = $img->rows * $img->cols;
    my %proportions = map { $_ => ($pixel_counts{$_} / $total_pixels) * 100 } keys %pixel_counts;

    # Plot stats
    my $graph = GD::Graph::bars->new(800, 600);
    $graph->set(
        x_label           => 'Categories',
        y_label           => 'Proportion (%)',
        title             => 'Schumann Resonance Stats',
        y_max_value       => 100,
        y_tick_number     => 10,
        bar_spacing       => 5,
    );
    my @data = ([keys %proportions], [values %proportions]);
    my $gd = $graph->plot(\@data) or die $graph->error;
    open my $fh, '>', 'graph.png' or die $!;
    binmode $fh;
    print $fh $gd->png;
    close $fh;

    print "Graph saved to 'graph.png'.\n";
}

# Main logic
my $img = load_image();
show_stats($img, \%color_ranges);
