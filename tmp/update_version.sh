#!/bin/bash

# Script to update the spec_version in runtime/src/lib.rs by incrementing it by 1

set -e

RUNTIME_FILE="runtime/src/lib.rs"

# Check if the runtime file exists
if [ ! -f "$RUNTIME_FILE" ]; then
    echo "Error: $RUNTIME_FILE not found!"
    exit 1
fi

# Extract current spec_version
current_version=$(grep -o 'spec_version: [0-9]\+' "$RUNTIME_FILE" | grep -o '[0-9]\+')

if [ -z "$current_version" ]; then
    echo "Error: Could not find spec_version in $RUNTIME_FILE"
    exit 1
fi

# Calculate new version
new_version=$((current_version + 1))

echo "Current spec_version: $current_version"
echo "New spec_version: $new_version"

# Update the version
sed -i "s/spec_version: $current_version,/spec_version: $new_version,/" "$RUNTIME_FILE"

# Verify the change
updated_version=$(grep -o 'spec_version: [0-9]\+' "$RUNTIME_FILE" | grep -o '[0-9]\+')

if [ "$updated_version" = "$new_version" ]; then
    echo "✅ Successfully updated spec_version from $current_version to $new_version"
else
    echo "❌ Failed to update spec_version. Restoring backup..."
    mv "$RUNTIME_FILE.bak" "$RUNTIME_FILE"
    exit 1
fi

git add "$RUNTIME_FILE"
git commit -m "bump version"
git push

echo "Done! Remember to commit the changes."
