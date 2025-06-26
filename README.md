# Draw Platform Puzzler - Infinite Edition

A platformer game where you can draw temporary platforms with your mouse to solve puzzles and reach the goal. Features infinite randomly generated levels with progressive difficulty and exciting new elements!

📝 **[Read the full development blog post](blog_post.md)** - Learn about the design process, technical challenges, and what makes this game special!

## Installation

1. Make sure you have Python installed
2. Install pygame: `pip install pygame` or `pip install -r requirements.txt`
3. Run the game: `python platformer_game.py`

## How to Play

### Controls
- **WASD** or **Arrow Keys**: Move the player
- **Space**: Jump
- **Mouse**: Click and drag to draw temporary platforms
- **R**: Reset current level
- **N**: Clear all drawn platforms
- **ESC**: Exit game
- **F11**: Toggle fullscreen mode

### Gameplay
- Navigate the blue character to the yellow goal with the red star
- Draw purple platforms by clicking and dragging with your mouse
- Drawn platforms are temporary and will fade away after 5 seconds
- You have a limited number of platforms you can draw per level
- Use your platforms strategically to solve each puzzle
- Collect gold diamonds for bonus points!
- Avoid red spikes - they'll reset your position

### Features
- **Infinite Randomly Generated Levels**: Never run out of challenges!
- **Progressive Difficulty**: Levels get harder as you advance
- **8 Different Level Types**: Each with unique challenges and mechanics
- **Animated Character**: Smooth walking, jumping, and directional animations with a cheerful, friendly design
- **Sketch Pad Aesthetic**: Clean grid background with sketch-like visual style
- **Platform Drawing System**: Click and drag to create platforms with visual feedback
- **Temporary Platforms**: Drawn platforms fade after 5 seconds with visual feedback
- **Dynamic Platform Limits**: More drawable platforms available in higher levels
- **Moving Platforms**: Light blue platforms that move back and forth
- **Spike Traps**: Dangerous red spikes that reset your position
- **Disappearing Platforms**: Orange platforms that vanish when stepped on
- **Collectibles**: Gold diamonds worth bonus points
- **Physics**: Realistic gravity and collision detection
- **Moving Platform Physics**: Player moves with moving platforms for realistic gameplay
- **Smart UI**: Compact UI elements positioned to never interfere with gameplay
- **Clear Separation**: Game area remains completely unobstructed while UI stays visible
- **Intuitive Layout**: Controls at top-left, game stats at top-right for easy reference

### Level Types
The game features 8 different types of randomly generated levels:

1. **Horizontal Gaps**: Cross large gaps using strategic platform placement
2. **Vertical Climb**: Climb high using multiple platforms efficiently  
3. **Mixed Challenge**: Combination of horizontal and vertical obstacles
4. **Maze Navigation**: Navigate through maze-like platform arrangements
5. **Timing Challenge**: Levels requiring precise timing and platform usage
6. **Moving Platforms**: Ride and time moving platforms to reach your goal
7. **Spike Gauntlet**: Navigate dangerous spike traps with careful planning
8. **Disappearing Platforms**: Race against time on platforms that vanish

### Progressive Difficulty
- **Levels 1-3**: Structured introduction to basic level types
- **Level 4+**: Random level types with increasing complexity including new mechanics
- **Platform Limit**: Starts at 2, increases every 2 levels (capped at reasonable limits)
- **Level Complexity**: More platforms, larger gaps, higher climbs as you progress
- **New Elements**: Moving platforms, spikes, and disappearing platforms appear in higher levels
- **Difficulty Cap**: Difficulty plateaus at level 10 to maintain playability

## Game Mechanics

### Drawing Platforms
- Click and drag with the left mouse button to draw a platform
- Platforms must be at least 30 pixels long to be created
- The preview line shows green when the platform is long enough, red when too short
- Platforms are created horizontally between your start and end points

### Platform Management
- Each level has a limit on how many platforms you can draw simultaneously
- Platform limits increase with level progression for added strategic depth
- Platforms automatically disappear after 5 seconds
- A timer shows how much time is left for each platform
- Use the 'N' key to clear all drawn platforms if you need to start over

### Special Elements
- **Moving Platforms (Light Blue)**: Move back and forth between set points - time your jumps!
- **Spike Traps (Red)**: Touching spikes resets your position - avoid at all costs!
- **Disappearing Platforms (Orange)**: Flash as a warning, then vanish when stepped on
- **Collectibles (Gold Diamonds)**: Collect for bonus points and bragging rights

### Physics
- The player has realistic gravity and momentum
- Jump only when on solid ground
- Collision detection works for all platform edges (top, bottom, sides)
- Moving platforms carry the player along

### Level Generation
- Each level is procedurally generated with carefully balanced challenges
- Goals are positioned to require strategic thinking and platform usage
- Level layouts ensure solvability while maintaining difficulty
- Special elements are introduced progressively
- No two playthroughs are exactly the same!

## Tips for Success
- Plan your platform placement before drawing
- Watch the timers - platforms disappear quickly!
- Use the minimum number of platforms needed
- Sometimes you need to wait for old platforms to disappear before drawing new ones
- Practice the timing - you might need to draw platforms while moving
- Learn the different level types and adapt your strategy accordingly
- Higher levels give you more platforms to work with, but also present greater challenges
- **Moving Platforms**: Time your jumps and sometimes ride them to reach distant areas
- **Spike Levels**: Plan safe routes and use platforms to bridge over dangerous areas
- **Disappearing Platforms**: Move quickly and have backup platforms ready
- **Collectibles**: Don't risk your life for points, but grab them when safe

## Level Type Strategies
- **Horizontal Gaps**: Focus on timing and distance - don't waste platforms on short jumps
- **Vertical Climb**: Plan your route upward, sometimes zigzagging is more efficient
- **Mixed Challenge**: Combine horizontal and vertical strategies
- **Maze Navigation**: Look for the optimal path before drawing any platforms
- **Timing Challenge**: These levels test your ability to draw platforms while moving
- **Moving Platforms**: Learn the movement patterns and time your approach
- **Spike Gauntlet**: Safety first - use platforms to create safe paths over danger
- **Disappearing Platforms**: Speed and backup plans are key to success

Enjoy the infinite puzzle-solving adventure with exciting new challenges!
