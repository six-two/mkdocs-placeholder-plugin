function generate_placeholder_password(length) {
    if (length < 8) {
        console.warn("Passwords should be at least 8 characters long");
    }

    // Alphanumeric characters, widely supported
    const pw_random_candidates = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

    // Generate the characters using the browser's API for "cryptographically strong random values"
    const pw_chars = [...window.crypto.getRandomValues(new Uint32Array(length))]
    // mostly safe. the first couple characters have a slightly higher possibility of being chosen
        .map((x) => pw_random_candidates[x % pw_random_candidates.length]);

    // Show estimated strength on the console
    const pw_strength = Math.floor(Math.log2(pw_random_candidates.length) * length);
    console.log(`Generated random password. Approximate real entropy: ${pw_strength} bits`);

    // return the random password
    return pw_chars.join("");
}
