#!/bin/bash

echo "🗺️  Social Mode Map Visualization"
echo "=================================="
echo ""

node << 'NODE_END'
const map = require('./packages/server/data/map/social_world.json');

const WIDTH = 48;
const HEIGHT = 48;
const spawnX = 26;
const spawnY = 12;

console.log('Map: 48x48 tiles');
console.log('Source: World region (432, 48)');
console.log('Spawn: (' + spawnX + ', ' + spawnY + ')');
console.log('');

// Show a portion of the map around spawn
const viewWidth = 20;
const viewHeight = 10;
const startX = Math.max(0, spawnX - Math.floor(viewWidth / 2));
const startY = Math.max(0, spawnY - Math.floor(viewHeight / 2));

console.log('Map view around spawn (' + viewWidth + 'x' + viewHeight + '):');
console.log('Legend: . = walkable, X = collision, S = spawn');
console.log('');

// Top border
let topLine = '  ';
for (let x = 0; x < viewWidth; x++) {
    topLine += String((startX + x) % 10);
}
console.log(topLine);

for (let y = 0; y < viewHeight; y++) {
    const worldY = startY + y;
    let line = String(worldY).padStart(2) + ' ';
    
    for (let x = 0; x < viewWidth; x++) {
        const worldX = startX + x;
        const idx = worldY * WIDTH + worldX;
        const isCollision = map.collisions.includes(idx);
        
        if (worldX === spawnX && worldY === spawnY) {
            line += 'S';
        } else if (isCollision) {
            line += 'X';
        } else {
            line += '.';
        }
    }
    console.log(line);
}

console.log('');
console.log('Map Statistics:');
console.log('  Total tiles: ' + map.data.length);
console.log('  Collision tiles: ' + map.collisions.length);
console.log('  Non-zero tiles: ' + map.data.filter(t => t > 0).length);
console.log('  Zero tiles: ' + map.data.filter(t => t === 0).length);
console.log('');

// Check spawn area
const spawnIdx = spawnY * WIDTH + spawnX;
console.log('Spawn Point Analysis:');
console.log('  Position: (' + spawnX + ', ' + spawnY + ')');
console.log('  Index: ' + spawnIdx);
console.log('  Tile value: ' + map.data[spawnIdx]);
console.log('  Is collision: ' + (map.collisions.includes(spawnIdx) ? 'YES ❌' : 'NO ✅'));
console.log('');

// Check walkable area around spawn
let walkableCount = 0;
let collisionCount = 0;
for (let dy = -2; dy <= 2; dy++) {
    for (let dx = -2; dx <= 2; dx++) {
        const checkX = spawnX + dx;
        const checkY = spawnY + dy;
        if (checkX >= 0 && checkX < WIDTH && checkY >= 0 && checkY < HEIGHT) {
            const checkIdx = checkY * WIDTH + checkX;
            if (map.collisions.includes(checkIdx)) {
                collisionCount++;
            } else {
                walkableCount++;
            }
        }
    }
}

console.log('5x5 area around spawn:');
console.log('  Walkable tiles: ' + walkableCount + ' ✅');
console.log('  Collision tiles: ' + collisionCount);
console.log('');

if (walkableCount >= 9) {
    console.log('✅ Spawn area is good - plenty of space to move!');
} else if (walkableCount >= 5) {
    console.log('⚠️  Spawn area is tight but should work');
} else {
    console.log('❌ Spawn area might be too cramped!');
}
NODE_END
