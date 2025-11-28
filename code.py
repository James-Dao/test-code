import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, host='localhost', database='test1', user='root', password=''):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                logger.info("成功连接到MySQL数据库")
        except Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("数据库连接已关闭")
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[int]:
        """执行查询并返回受影响的行数"""
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            logger.info(f"查询执行成功: {query}")
            return cursor.rowcount
        except Error as e:
            logger.error(f"查询执行失败: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询并返回所有结果"""
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            return result
        except Error as e:
            logger.error(f"数据获取失败: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """执行查询并返回单条结果"""
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return result
        except Error as e:
            logger.error(f"数据获取失败: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

class UserService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_user(self, username: str, email: str, password: str, 
                   full_name: str = None, phone: str = None) -> int:
        """创建新用户"""
        query = """
        INSERT INTO users (username, email, password, full_name, phone)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (username, email, password, full_name, phone)
        result = self.db.execute_query(query, params)
        return result
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        query = "SELECT * FROM users WHERE user_id = %s"
        return self.db.fetch_one(query, (user_id,))
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        query = "SELECT * FROM users WHERE username = %s"
        return self.db.fetch_one(query, (username,))
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        query = "SELECT * FROM users WHERE email = %s"
        return self.db.fetch_one(query, (email,))
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户"""
        query = "SELECT * FROM users ORDER BY created_at DESC"
        return self.db.fetch_all(query)
    
    def update_user(self, user_id: int, **kwargs) -> int:
        """更新用户信息"""
        if not kwargs:
            return 0
        
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        query = f"UPDATE users SET {set_clause} WHERE user_id = %s"
        params = tuple(kwargs.values()) + (user_id,)
        
        return self.db.execute_query(query, params)
    
    def delete_user(self, user_id: int) -> int:
        """删除用户"""
        query = "DELETE FROM users WHERE user_id = %s"
        return self.db.execute_query(query, (user_id,))
    
    def change_password(self, user_id: int, new_password: str) -> int:
        """修改用户密码"""
        query = "UPDATE users SET password = %s WHERE user_id = %s"
        return self.db.execute_query(query, (new_password, user_id))

class CategoryService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_category(self, category_name: str, parent_id: int = None, 
                       description: str = None) -> int:
        """创建分类"""
        query = """
        INSERT INTO categories (category_name, parent_id, description)
        VALUES (%s, %s, %s)
        """
        params = (category_name, parent_id, description)
        return self.db.execute_query(query, params)
    
    def get_category_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取分类"""
        query = "SELECT * FROM categories WHERE category_id = %s"
        return self.db.fetch_one(query, (category_id,))
    
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """获取所有分类"""
        query = "SELECT * FROM categories ORDER BY category_name"
        return self.db.fetch_all(query)
    
    def get_subcategories(self, parent_id: int) -> List[Dict[str, Any]]:
        """获取指定父分类的子分类"""
        query = "SELECT * FROM categories WHERE parent_id = %s ORDER BY category_name"
        return self.db.fetch_all(query, (parent_id,))
    
    def get_root_categories(self) -> List[Dict[str, Any]]:
        """获取所有一级分类（没有父分类的分类）"""
        query = "SELECT * FROM categories WHERE parent_id IS NULL ORDER BY category_name"
        return self.db.fetch_all(query)
    
    def update_category(self, category_id: int, **kwargs) -> int:
        """更新分类信息"""
        if not kwargs:
            return 0
        
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        query = f"UPDATE categories SET {set_clause} WHERE category_id = %s"
        params = tuple(kwargs.values()) + (category_id,)
        
        return self.db.execute_query(query, params)
    
    def delete_category(self, category_id: int) -> int:
        """删除分类"""
        query = "DELETE FROM categories WHERE category_id = %s"
        return self.db.execute_query(query, (category_id,))

class ProductService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_product(self, product_name: str, price: float, category_id: int,
                      description: str = None, stock_quantity: int = 0) -> int:
        """创建商品"""
        query = """
        INSERT INTO products (product_name, description, price, stock_quantity, category_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (product_name, description, price, stock_quantity, category_id)
        return self.db.execute_query(query, params)
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取商品"""
        query = """
        SELECT p.*, c.category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.category_id 
        WHERE p.product_id = %s
        """
        return self.db.fetch_one(query, (product_id,))
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """获取所有商品"""
        query = """
        SELECT p.*, c.category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.category_id 
        ORDER BY p.created_at DESC
        """
        return self.db.fetch_all(query)
    
    def get_products_by_category(self, category_id: int) -> List[Dict[str, Any]]:
        """根据分类获取商品"""
        query = """
        SELECT p.*, c.category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.category_id 
        WHERE p.category_id = %s 
        ORDER BY p.product_name
        """
        return self.db.fetch_all(query, (category_id,))
    
    def search_products(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索商品"""
        query = """
        SELECT p.*, c.category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.category_id 
        WHERE p.product_name LIKE %s OR p.description LIKE %s 
        ORDER BY p.product_name
        """
        search_term = f"%{keyword}%"
        return self.db.fetch_all(query, (search_term, search_term))
    
    def update_product(self, product_id: int, **kwargs) -> int:
        """更新商品信息"""
        if not kwargs:
            return 0
        
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        query = f"UPDATE products SET {set_clause} WHERE product_id = %s"
        params = tuple(kwargs.values()) + (product_id,)
        
        return self.db.execute_query(query, params)
    
    def update_stock(self, product_id: int, new_quantity: int) -> int:
        """更新商品库存"""
        query = "UPDATE products SET stock_quantity = %s WHERE product_id = %s"
        return self.db.execute_query(query, (new_quantity, product_id))
    
    def delete_product(self, product_id: int) -> int:
        """删除商品"""
        query = "DELETE FROM products WHERE product_id = %s"
        return self.db.execute_query(query, (product_id,))

class OrderService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_order(self, user_id: int, total_amount: float, 
                    shipping_address: str, status: str = 'pending') -> int:
        """创建订单"""
        query = """
        INSERT INTO orders (user_id, total_amount, status, shipping_address)
        VALUES (%s, %s, %s, %s)
        """
        params = (user_id, total_amount, status, shipping_address)
        return self.db.execute_query(query, params)
    
    def get_order_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取订单"""
        query = """
        SELECT o.*, u.username, u.full_name 
        FROM orders o 
        LEFT JOIN users u ON o.user_id = u.user_id 
        WHERE o.order_id = %s
        """
        return self.db.fetch_one(query, (order_id,))
    
    def get_orders_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户的订单"""
        query = """
        SELECT o.*, u.username, u.full_name 
        FROM orders o 
        LEFT JOIN users u ON o.user_id = u.user_id 
        WHERE o.user_id = %s 
        ORDER BY o.order_date DESC
        """
        return self.db.fetch_all(query, (user_id,))
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """获取所有订单"""
        query = """
        SELECT o.*, u.username, u.full_name 
        FROM orders o 
        LEFT JOIN users u ON o.user_id = u.user_id 
        ORDER BY o.order_date DESC
        """
        return self.db.fetch_all(query)
    
    def update_order_status(self, order_id: int, new_status: str) -> int:
        """更新订单状态"""
        query = "UPDATE orders SET status = %s WHERE order_id = %s"
        return self.db.execute_query(query, (new_status, order_id))
    
    def delete_order(self, order_id: int) -> int:
        """删除订单"""
        query = "DELETE FROM orders WHERE order_id = %s"
        return self.db.execute_query(query, (order_id,))

class OrderItemService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def add_order_item(self, order_id: int, product_id: int, 
                      quantity: int, unit_price: float) -> int:
        """添加订单项"""
        query = """
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        VALUES (%s, %s, %s, %s)
        """
        params = (order_id, product_id, quantity, unit_price)
        return self.db.execute_query(query, params)
    
    def get_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        """获取订单的所有商品项"""
        query = """
        SELECT oi.*, p.product_name, p.description 
        FROM order_items oi 
        LEFT JOIN products p ON oi.product_id = p.product_id 
        WHERE oi.order_id = %s
        """
        return self.db.fetch_all(query, (order_id,))
    
    def update_order_item_quantity(self, order_item_id: int, new_quantity: int) -> int:
        """更新订单项数量"""
        query = "UPDATE order_items SET quantity = %s WHERE order_item_id = %s"
        return self.db.execute_query(query, (new_quantity, order_item_id))
    
    def delete_order_item(self, order_item_id: int) -> int:
        """删除订单项"""
        query = "DELETE FROM order_items WHERE order_item_id = %s"
        return self.db.execute_query(query, (order_item_id,))
    
    def get_order_total_amount(self, order_id: int) -> float:
        """计算订单总金额"""
        query = "SELECT SUM(subtotal) as total FROM order_items WHERE order_id = %s"
        result = self.db.fetch_one(query, (order_id,))
        return result['total'] if result and result['total'] else 0.0

class ECommerceService:
    """综合电商服务类，提供完整的业务流程"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.user_service = UserService(db_manager)
        self.category_service = CategoryService(db_manager)
        self.product_service = ProductService(db_manager)
        self.order_service = OrderService(db_manager)
        self.order_item_service = OrderItemService(db_manager)
    
    def place_order(self, user_id: int, items: List[Dict], shipping_address: str) -> int:
        """下订单完整流程"""
        try:
            # 开始事务
            self.db.connection.start_transaction()
            
            # 计算总金额
            total_amount = sum(item['quantity'] * item['unit_price'] for item in items)
            
            # 创建订单
            order_id = self.order_service.create_order(user_id, total_amount, shipping_address)
            
            # 添加订单项
            for item in items:
                self.order_item_service.add_order_item(
                    order_id, item['product_id'], item['quantity'], item['unit_price']
                )
            
            # 提交事务
            self.db.connection.commit()
            logger.info(f"订单创建成功: 订单ID {order_id}, 总金额 {total_amount}")
            return order_id
            
        except Exception as e:
            # 回滚事务
            self.db.connection.rollback()
            logger.error(f"下单失败: {e}")
            raise
    
    def get_user_order_history(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户的完整订单历史"""
        orders = self.order_service.get_orders_by_user(user_id)
        
        for order in orders:
            order['items'] = self.order_item_service.get_order_items(order['order_id'])
        
        return orders

# 使用示例
def main():
    # 初始化数据库管理器
    db_manager = DatabaseManager(
        host='localhost',
        database='test1', 
        user='root',
        password='your_password'  # 请替换为实际密码
    )
    
    try:
        # 连接数据库
        db_manager.connect()
        
        # 初始化服务
        ecommerce = ECommerceService(db_manager)
        
        # 示例：获取所有用户
        users = ecommerce.user_service.get_all_users()
        print("所有用户:", len(users))
        
        # 示例：获取所有商品
        products = ecommerce.product_service.get_all_products()
        print("所有商品:", len(products))
        
        # 示例：获取所有订单
        orders = ecommerce.order_service.get_all_orders()
        print("所有订单:", len(orders))
        
    except Exception as e:
        print(f"操作失败: {e}")
    finally:
        # 关闭连接
        db_manager.disconnect()

if __name__ == "__main__":
    main()