<?php
// Writes the "Vom Laster gefallen" branding into BookStack's settings.
// Runs on every container start (see 50-apply-branding.sh), so this file is
// the source of truth: changes made under Settings > Customization for these
// keys are overwritten on the next restart.

require '/app/www/vendor/autoload.php';
$app = require '/app/www/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

$settings = [
    'app-name'              => 'Vom Laster gefallen',
    'app-name-header'       => 'false', // the logo already contains the name
    'app-logo'              => '/branding/logo-header-500.png',
    'app-icon'              => '/branding/icon-256.png',
    'app-icon-180'          => '/branding/icon-180.png',
    'app-icon-128'          => '/branding/icon-128.png',
    'app-icon-64'           => '/branding/icon-64.png',
    'app-icon-32'           => '/branding/icon-32.png',
    'app-color'             => '#c2410c', 'app-color-light'       => 'rgba(194,65,12,0.15)',
    'link-color'            => '#0e7490',
    'app-color-dark'        => '#ea580c', 'app-color-light-dark'  => 'rgba(234,88,12,0.15)',
    'link-color-dark'       => '#22b8cf',
    'bookshelf-color'       => '#8a5a2b', 'bookshelf-color-dark'  => '#c8955f',
    'book-color'            => '#c2410c', 'book-color-dark'       => '#f0803c',
    'chapter-color'         => '#a16207', 'chapter-color-dark'    => '#e0a82e',
    'page-color'            => '#0e7490', 'page-color-dark'       => '#3cc6db',
    'page-draft-color'      => '#7c3aed', 'page-draft-color-dark' => '#a78bfa',
];

foreach ($settings as $key => $value) {
    setting()->put($key, $value);
}
echo 'applied ' . count($settings) . " branding settings\n";
