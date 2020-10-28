UniGet will download all of the latest configs from Unimus allowing use of linux search functions rather than only Unimus ones.

Run with sudo priviledges as this script will need to access /etc/hosts which will substitute the addresses with the filenames (the filenames are drawn from their description in Unimus). Simply ssh to the config's filename to ssh to the device.

Requirements:

-token.txt file with the API token (User management > API Tokens)

-url.txt file with the URL of Unimus (EX. https://example.unimus.net)
