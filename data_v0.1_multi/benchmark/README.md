# AgentWorld Multi-Agent Cooperation Benchmark

A comprehensive benchmark suite containing 15 multi-agent cooperative tasks designed to evaluate AI agents' coordination, crafting, and collaboration capabilities in complex gaming environments.

## 📋 Task Overview

### **Basic Crafting Series (Tasks 1-5)**
- **Task 1**: Magic Staff Crafting - Wood Collection → Stick Creation → Staff Assembly
- **Task 2**: Arrow Mass Production - Material Gathering → Large-scale Manufacturing → Quality Control
- **Task 3**: Silver Ring Forging - Ore Mining → Metal Smelting → Ring Smithing
- **Task 4**: Emerald Ring Crafting - Gem Mining + Metal Crafting → Jewelry Assembly
- **Task 5**: Beryl Pendant Creation - Plant Foraging + Gem Mining → Accessory Crafting

### **Intermediate Crafting Series (Tasks 6-10)**
- **Task 6**: Heavy Sword Forging - Large-scale Mining → Multi-step Smelting → Weapon Assembly
- **Task 7**: Pickaxe Tool Creation - Bulk Material Collection → Industrial Smelting → Advanced Tools
- **Task 8**: Bronze Alloy Production - Specialized Ore Mining → Alloy Metallurgy
- **Task 9**: Topaz Ring Crafting - Precious Material Handling → Luxury Item Creation
- **Task 10**: Stew Cooking - Container Crafting + Ingredient Gathering → Culinary Arts

### **Advanced Crafting Series (Tasks 11-15)**
- **Task 11**: Lightning Staff Enhancement - Basic Crafting + Elemental Materials → Magical Enhancement
- **Task 12**: Gold Ring Creation - Precious Metal Mining → High-difficulty Smelting
- **Task 13**: Bucket Crafting - Large-scale Lumbering → Advanced Container Production
- **Task 14**: Shrimp Cooking - Fishing Operations → Seafood Culinary Arts
- **Task 15**: Jellyfish Smoothie - Advanced Fishing + Specialized Containers → Exotic Beverages

## ✅ Configuration Validation Report

### **Basic Structure Validation**
- ✅ All 15 task files successfully created
- ✅ Each task has 3 agent configurations
- ✅ Consistent action step limit: 25 steps
- ✅ Complete success criteria definitions
- ✅ No YAML syntax errors

### **Game Mechanics Consistency**
- ✅ Crafting recipes match game data
- ✅ Skill level requirements align with game systems
- ✅ Material requirements based on actual game items
- ✅ Tool and equipment configurations are correct

### **Skill Level Distribution**
```
Basic Skills (Level 1): Lumberjacking, Smithing, Crafting, Fishing
Intermediate Skills (Level 5-15): Container Crafting, Gem Mining, Cooking
Advanced Skills (Level 20+): Metal Smelting, Precious Metal Mining
Expert Skills (Level 25+): Gold Mining, Advanced Gem Mining
Master Skills (Level 57+): Emerald Mining
```

### **Cooperation Mode Validation**
- ✅ All tasks follow "Collection → Processing → Crafting" three-stage structure
- ✅ Clear role division and responsibilities
- ✅ Safe material transfer mechanisms
- ✅ Global chat coordination system

## 🎯 Difficulty Gradient Design

### **Beginner Tasks (1-5)**
- **Characteristics**: Basic materials, simple processes, low skill requirements
- **Learning Objectives**: Basic cooperation, material transfer, simple crafting

### **Intermediate Tasks (6-10)**
- **Characteristics**: Composite materials, multi-step processes, moderate skill requirements
- **Learning Objectives**: Complex coordination, resource management, quality control

### **Advanced Tasks (11-15)**
- **Characteristics**: Rare materials, advanced processes, specialized skill requirements
- **Learning Objectives**: Precise coordination, risk management, professional expertise

## 🔧 Technical Specifications

### **Agent Configuration Standards**
- **Skill Distribution**: Each agent specializes in 2-4 related skills
- **Equipment Setup**: Provides necessary basic tools for tasks
- **Starting Positions**: Distributed across relevant areas in the game world
- **Inventory Items**: Basic supplies (potions, food)

### **Task Flow Design**
1. **Initialization**: Agents start at designated positions
2. **Coordination Phase**: Establish cooperation through global chat
3. **Execution Phase**: Parallel/sequential execution of specialized tasks
4. **Transfer Phase**: Safe transfer of intermediate products
5. **Completion Phase**: Final product creation and verification

## 📊 Evaluation Dimensions

### **Cooperation Capabilities**
- Communication efficiency
- Task coordination
- Time management
- Conflict resolution

### **Technical Abilities**
- Skill application
- Tool usage
- Crafting precision
- Quality control

### **Adaptability**
- Environment exploration
- Resource discovery
- Failure recovery
- Strategy adjustment

## 🚀 Usage Instructions

### **Running Tasks**
```bash
# Run a single task
python run_task.py --task benchmark/task_01_magic_staff.yaml

# Batch run basic tasks
python run_benchmark.py --range 1-5

# Run complete benchmark suite
python run_benchmark.py --all
```

### **Result Analysis**
Each task execution generates:
- Execution logs
- Performance metrics
- Cooperation scores
- Failure analysis

## 📈 Benchmark Value

### **Research Value**
- **Multi-Agent Coordination**: Evaluate inter-agent collaboration capabilities
- **Complex Task Planning**: Test long-term goal-oriented planning
- **Dynamic Adaptation**: Verify adaptability to environmental changes
- **Knowledge Application**: Examine domain knowledge application levels

### **Development Value**
- **Capability Assessment**: Objectively evaluate AI agent development levels
- **Algorithm Optimization**: Identify improvement directions and bottlenecks
- **System Testing**: Verify multi-agent system stability
- **User Experience**: Assess human-computer interaction quality

## 📝 Maintenance Notes

### **Configuration Updates**
- Update recipes synchronously when game balance adjustments are made
- Expand task sets when new skills or items are added
- Adjust difficulty gradients based on test results

### **Quality Assurance**
- Regularly verify task executability
- Monitor success rates and completion times
- Collect user feedback for optimization

---

*This benchmark suite provides a standardized evaluation framework for multi-agent AI research, helping to advance development and progress in this field.*
