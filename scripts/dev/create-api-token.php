<?php
/**
 * DEV/CI ONLY. Creates a BookStack API token for an existing user and prints
 * "token_id:secret" to stdout. Mirrors UserApiTokenController::store().
 *
 * Runs inside the bookstack container:
 *   php create-api-token.php <user-email> <token-name> <expires Y-m-d>
 *
 * In production, create tokens in the UI (user profile → API Tokens).
 */

use BookStack\Api\ApiToken;
use BookStack\Users\Models\User;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

[$_, $email, $name, $expires] = array_pad($argv, 4, null);
if (!$email || !$name || !$expires || !preg_match('/^\d{4}-\d{2}-\d{2}$/', $expires)) {
    fwrite(STDERR, "usage: php create-api-token.php <user-email> <token-name> <YYYY-MM-DD>\n");
    exit(2);
}

require '/app/www/vendor/autoload.php';
$app = require '/app/www/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

$user = User::query()->where('email', '=', $email)->first();
if (!$user) {
    fwrite(STDERR, "no user with email {$email}\n");
    exit(1);
}

$secret = Str::random(32);
$token = (new ApiToken())->forceFill([
    'name'       => $name,
    'token_id'   => Str::random(32),
    'secret'     => Hash::make($secret),
    'user_id'    => $user->id,
    'expires_at' => $expires,
]);
while (ApiToken::query()->where('token_id', '=', $token->token_id)->exists()) {
    $token->token_id = Str::random(32);
}
$token->save();

echo $token->token_id . ':' . $secret . "\n";
