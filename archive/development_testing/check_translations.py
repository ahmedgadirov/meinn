#!/usr/bin/env python3

import sqlite3

def check_translations():
    print("Checking translations in database...")
    
    conn = sqlite3.connect('menu_data.db')
    cursor = conn.cursor()
    
    # Check categories with translations
    cursor.execute('SELECT id, name, name_az, name_en, name_ru, name_tr FROM categories LIMIT 3')
    rows = cursor.fetchall()
    print('Categories with translations:')
    for row in rows:
        print(f'  ID: {row[0]}')
        print(f'    Default: {row[1]}')
        print(f'    AZ: {row[2]}')
        print(f'    EN: {row[3]}')
        print(f'    RU: {row[4]}')
        print(f'    TR: {row[5]}')
        print()
    
    # Check menu items with translations
    cursor.execute('SELECT id, name, name_az, name_en, name_ru, name_tr FROM menu_items LIMIT 2')
    rows = cursor.fetchall()
    print('Menu items with translations:')
    for row in rows:
        print(f'  ID: {row[0]}')
        print(f'    Default: {row[1]}')
        print(f'    AZ: {row[2]}')
        print(f'    EN: {row[3]}')
        print(f'    RU: {row[4]}')
        print(f'    TR: {row[5]}')
        print()
    
    conn.close()

if __name__ == "__main__":
    check_translations()
