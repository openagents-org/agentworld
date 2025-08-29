#!/usr/bin/env python3
"""
重新分析tile数据结构，确认1392是否真的是tile index
"""

import json

def analyze_tile_data():
    print("🔍 重新分析地图数据结构...")
    
    try:
        with open('/home/ubuntu/works/agentworld/packages/server/data/map/world.json', 'r') as f:
            map_data = json.load(f)
        
        print(f"📊 地图基本信息:")
        print(f"   - 版本: {map_data.get('version')}")
        print(f"   - 宽度: {map_data.get('width')} tiles")
        print(f"   - 高度: {map_data.get('height')} tiles")
        print(f"   - 瓦片大小: {map_data.get('tileSize')} pixels")
        
        # 分析rocks数据结构
        rocks = map_data.get('rocks', [])
        print(f"\n⛏️  岩石数据结构分析:")
        print(f"   - 总数: {len(rocks)} 个岩石")
        
        # 找到iron rock
        iron_rock = None
        for rock in rocks:
            if rock.get('type') == 'iron':
                iron_rock = rock
                break
        
        if iron_rock:
            print(f"\n🎯 Iron Rock 数据详情:")
            print("=" * 50)
            for key, value in iron_rock.items():
                print(f"   {key}: {value}")
            print("=" * 50)
            
            # 重新分析data字段
            data_field = iron_rock.get('data', [])
            print(f"\n🔍 深度分析'data'字段:")
            print(f"   - 类型: {type(data_field)}")
            print(f"   - 值: {data_field}")
            
            if isinstance(data_field, list) and data_field:
                value = data_field[0]
                print(f"   - 第一个值: {value}")
                print(f"   - 值类型: {type(value)}")
                
                # 检查这个值是否真的是tile index
                if isinstance(value, int):
                    map_width = map_data.get('width', 1056)
                    map_height = map_data.get('height', 768)
                    max_tile_index = map_width * map_height - 1
                    
                    print(f"\n📐 Tile Index 验证:")
                    print(f"   - 地图最大tile index: {max_tile_index}")
                    print(f"   - 当前值 {value} 是否在范围内: {0 <= value <= max_tile_index}")
                    
                    if 0 <= value <= max_tile_index:
                        x = value % map_width
                        y = value // map_width
                        print(f"   - 如果是tile index，坐标为: ({x}, {y})")
                        print(f"   - Y坐标是否合理: {'是' if 0 <= y < map_height else '否'}")
                    else:
                        print(f"   - ❌ 值 {value} 超出tile index范围，可能不是tile index")
        
        # 比较其他岩石的data值
        print(f"\n📊 所有岩石的data值比较:")
        print("=" * 60)
        print(f"{'类型':<12} {'Data值':<15} {'可能是Tile Index?'}")
        print("-" * 60)
        
        map_width = map_data.get('width', 1056)
        map_height = map_data.get('height', 768)
        max_tile_index = map_width * map_height - 1
        
        for rock in rocks:
            rock_type = rock.get('type', 'unknown')
            data = rock.get('data', [])
            
            if data and isinstance(data, list):
                for i, value in enumerate(data):
                    if isinstance(value, int):
                        is_valid_tile = 0 <= value <= max_tile_index
                        status = "✅ 可能" if is_valid_tile else "❌ 不太可能"
                        
                        if i == 0:  # 只显示第一个值
                            print(f"{rock_type:<12} {str(data):<15} {status}")
                        
                        if rock_type == 'iron':
                            print(f"   🎯 Iron详情: 值={value}, 范围内={is_valid_tile}")
                            if is_valid_tile:
                                x = value % map_width
                                y = value // map_width
                                print(f"      计算坐标: ({x}, {y})")
        
        # 检查是否有其他可能的坐标数据
        print(f"\n🔍 寻找其他可能的坐标信息:")
        
        # 检查是否有直接的x, y字段
        has_xy_coords = False
        for rock in rocks[:3]:  # 检查前几个
            if 'x' in rock or 'y' in rock:
                has_xy_coords = True
                print(f"   发现直接坐标字段:")
                for key, value in rock.items():
                    if key in ['x', 'y', 'position', 'location']:
                        print(f"      {key}: {value}")
        
        if not has_xy_coords:
            print(f"   ❌ 没有发现直接的x,y坐标字段")
            print(f"   ✅ data字段很可能确实是tile IDs")
        
        # 分析地图data字段的结构
        map_data_field = map_data.get('data', [])
        if map_data_field:
            print(f"\n🗺️  地图data字段分析:")
            print(f"   - 类型: {type(map_data_field)}")
            print(f"   - 长度: {len(map_data_field) if isinstance(map_data_field, list) else 'N/A'}")
            
            if isinstance(map_data_field, list) and len(map_data_field) > 1392:
                sample_tile = map_data_field[1392] if len(map_data_field) > 1392 else None
                print(f"   - 位置1392的瓦片数据: {sample_tile}")
                print(f"   - 这可能证实1392确实是一个有效的tile index")
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_tile_data()
