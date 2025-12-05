from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from models import (
    init_database, get_all_dishes, add_dish, 
    get_dishes_by_category, add_favorite, 
    get_all_favorites, delete_favorite
)

app = Flask(__name__)
CORS(app)

init_database()

@app.route('/api/dishes', methods=['GET'])
def get_dishes():
    try:
        dishes = get_all_dishes()
        return jsonify({
            'success': True,
            'data': dishes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/dishes', methods=['POST'])
def create_dish():
    try:
        data = request.json
        name = data.get('name')
        category = data.get('category')
        
        if not name or not category:
            return jsonify({
                'success': False,
                'message': '菜品名称和分类不能为空'
            }), 400
        
        if category not in ['dish', 'soup']:
            return jsonify({
                'success': False,
                'message': '分类必须是dish(菜)或soup(汤)'
            }), 400
        
        dish_id = add_dish(name, category, is_preset=0)
        return jsonify({
            'success': True,
            'data': {
                'id': dish_id,
                'name': name,
                'category': category
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/generate-menu', methods=['GET'])
def generate_menu():
    try:
        dishes = get_dishes_by_category('dish')
        soups = get_dishes_by_category('soup')
        
        if len(dishes) < 3:
            return jsonify({
                'success': False,
                'message': '菜品库中的菜不足3道，无法生成菜单'
            }), 400
        
        if len(soups) < 1:
            return jsonify({
                'success': False,
                'message': '菜品库中没有汤，无法生成菜单'
            }), 400
        
        selected_dishes = random.sample(dishes, 3)
        selected_soup = random.choice(soups)
        
        menu = {
            'dishes': [
                {'id': d['id'], 'name': d['name']} for d in selected_dishes
            ],
            'soup': {
                'id': selected_soup['id'],
                'name': selected_soup['name']
            }
        }
        
        return jsonify({
            'success': True,
            'data': menu
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/favorites', methods=['POST'])
def create_favorite():
    try:
        data = request.json
        menu_data = data.get('menu')
        
        if not menu_data:
            return jsonify({
                'success': False,
                'message': '菜单数据不能为空'
            }), 400
        
        favorite_id = add_favorite(menu_data)
        return jsonify({
            'success': True,
            'data': {
                'id': favorite_id
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    try:
        favorites = get_all_favorites()
        return jsonify({
            'success': True,
            'data': favorites
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/favorites/<int:favorite_id>', methods=['DELETE'])
def remove_favorite(favorite_id):
    try:
        delete_favorite(favorite_id)
        return jsonify({
            'success': True,
            'message': '删除成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
