"""
FastAPI API端点定义
为code.py中的服务类提供RESTful API接口
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import code
from code import DatabaseManager, ECommerceService
from .api import UserCreateRequest,UserUpdateRequest,UserResponse,CategoryCreateRequest,CategoryUpdateRequest,CategoryResponse, ProductCreateRequest, ProductUpdateRequest, ProductResponse, OrderItemRequest, OrderCreateRequest, OrderResponse, OrderItemResponse, ChangePasswordRequest, SearchRequest, UpdateStockRequest, UpdateOrderStatusRequest


app = FastAPI(title="E-Commerce API", version="1.0.0", description="电商系统API接口")

# 全局数据库管理器（实际应用中应该使用依赖注入）
db_manager = None
ecommerce_service = None

def get_db_manager():
    """获取数据库管理器"""
    global db_manager
    if db_manager is None:
        db_manager = code.DatabaseManager(
            host='localhost',
            database='test1',
            user='root',
            password=''
        )
        db_manager.connect()
    return db_manager

def get_ecommerce_service():
    """获取电商服务"""
    global ecommerce_service
    if ecommerce_service is None:
        db = get_db_manager()
        ecommerce_service = code.ECommerceService(db)
    return ecommerce_service

# ============================================================================
# 用户相关API端点
# ============================================================================

@app.post("/users", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_user(request: UserCreateRequest):
    """创建新用户"""
    try:
        service = get_ecommerce_service()
        user_id = service.user_service.create_user(
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            phone=request.phone
        )
        return {"message": "用户创建成功", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """根据ID获取用户"""
    try:
        service = get_ecommerce_service()
        user = service.user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users", response_model=List[UserResponse])
def get_all_users():
    """获取所有用户"""
    try:
        service = get_ecommerce_service()
        users = service.user_service.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/username/{username}", response_model=UserResponse)
def get_user_by_username(username: str):
    """根据用户名获取用户"""
    try:
        service = get_ecommerce_service()
        user = service.user_service.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/email/{email}", response_model=UserResponse)
def get_user_by_email(email: str):
    """根据邮箱获取用户"""
    try:
        service = get_ecommerce_service()
        user = service.user_service.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/{user_id}", response_model=Dict[str, Any])
def update_user(user_id: int, request: UserUpdateRequest):
    """更新用户信息"""
    try:
        service = get_ecommerce_service()
        update_data = request.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="没有提供更新数据")
        
        result = service.user_service.update_user(user_id, **update_data)
        return {"message": "用户更新成功", "affected_rows": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    """删除用户"""
    try:
        service = get_ecommerce_service()
        result = service.user_service.delete_user(user_id)
        if result == 0:
            raise HTTPException(status_code=404, detail="用户不存在")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/{user_id}/password", response_model=Dict[str, Any])
def change_password(user_id: int, request: ChangePasswordRequest):
    """修改用户密码"""
    try:
        service = get_ecommerce_service()
        result = service.user_service.change_password(user_id, request.new_password)
        return {"message": "密码修改成功", "affected_rows": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 分类相关API端点
# ============================================================================

@app.post("/categories", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_category(request: CategoryCreateRequest):
    """创建分类"""
    try:
        service = get_ecommerce_service()
        category_id = service.category_service.create_category(
            category_name=request.category_name,
            parent_id=request.parent_id,
            description=request.description
        )
        return {"message": "分类创建成功", "category_id": category_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int):
    """根据ID获取分类"""
    try:
        service = get_ecommerce_service()
        category = service.category_service.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories", response_model=List[CategoryResponse])
def get_all_categories():
    """获取所有分类"""
    try:
        service = get_ecommerce_service()
        categories = service.category_service.get_all_categories()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories/root", response_model=List[CategoryResponse])
def get_root_categories():
    """获取所有一级分类"""
    try:
        service = get_ecommerce_service()
        categories = service.category_service.get_root_categories()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories/{parent_id}/children", response_model=List[CategoryResponse])
def get_subcategories(parent_id: int):
    """获取指定父分类的子分类"""
    try:
        service = get_ecommerce_service()
        categories = service.category_service.get_subcategories(parent_id)
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/categories/{category_id}", response_model=Dict[str, Any])
def update_category(category_id: int, request: CategoryUpdateRequest):
    """更新分类信息"""
    try:
        service = get_ecommerce_service()
        update_data = request.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="没有提供更新数据")
        
        result = service.category_service.update_category(category_id, **update_data)
        return {"message": "分类更新成功", "affected_rows": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int):
    """删除分类"""
    try:
        service = get_ecommerce_service()
        result = service.category_service.delete_category(category_id)
        if result == 0:
            raise HTTPException(status_code=404, detail="分类不存在")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 商品相关API端点
# ============================================================================

@app.post("/products", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_product(request: ProductCreateRequest):
    """创建商品"""
    try:
        service = get_ecommerce_service()
        product_id = service.product_service.create_product(
            product_name=request.product_name,
            price=request.price,
            category_id=request.category_id,
            description=request.description,
            stock_quantity=request.stock_quantity
        )
        return {"message": "商品创建成功", "product_id": product_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    """根据ID获取商品"""
    try:
        service = get_ecommerce_service()
        product = service.product_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products", response_model=List[ProductResponse])
def get_all_products():
    """获取所有商品"""
    try:
        service = get_ecommerce_service()
        products = service.product_service.get_all_products()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/category/{category_id}", response_model=List[ProductResponse])
def get_products_by_category(category_id: int):
    """根据分类获取商品"""
    try:
        service = get_ecommerce_service()
        products = service.product_service.get_products_by_category(category_id)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/products/search", response_model=List[ProductResponse])
def search_products(request: SearchRequest):
    """搜索商品"""
    try:
        service = get_ecommerce_service()
        products = service.product_service.search_products(request.keyword)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/products/{product_id}", response_model=Dict[str, Any])
def update_product(product_id: int, request: ProductUpdateRequest):
    """更新商品信息"""
    try:
        service = get_ecommerce_service()
        update_data = request.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="没有提供更新数据")
        
        result = service.product_service.update_product(product_id, **update_data)
        return {"message": "商品更新成功", "affected_rows": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/products/{product_id}/stock", response_model=Dict[str, Any])
def update_product_stock(product_id: int, request: UpdateStockRequest):
    """更新商品库存"""
    try:
        service = get_ecommerce_service()
        result = service.product_service.update_stock(product_id, request.stock_quantity)
        return {"message": "库存更新成功", "affected_rows": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    """删除商品"""
    try:
        service = get_ecommerce_service()
        result = service.product_service.delete_product(product_id)
        if result == 0:
            raise HTTPException(status_code=404, detail="商品不存在")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 订单相关API端点
# ============================================================================

@app.post("/orders", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_order(request: OrderCreateRequest):
    """创建订单"""
    try:
        service = get_ecommerce_service()
        # 构建订单项
        items = [
            {"product_id": item.product_id, "quantity": item.quantity, "unit_price": item.unit_price}
            for item in request.items
        ]
        order_id = service.place_order(
            user_id=request.user_id,
            items=items,
            shipping_address=request.shipping_address
        )
        return {"message": "订单创建成功", "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    """根据ID获取订单"""
    try:
        service = get_ecommerce_service()
        order = service.order_service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders", response_model=List[OrderResponse])
def get_all_orders():
    """获取所有订单"""
    try:
        service = get_ecommerce_service()
        orders = service.order_service.get_all_orders()
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/user/{user_id}", response_model=List[OrderResponse])
def get_orders_by_user(user_id: int):
    """获取用户的订单"""
    try:
        service = get_ecommerce_service()
        orders = service.order_service.get_orders_by_user(user_id)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/user/{user_id}/history", response_model=List[Dict[str, Any]])
def get_user_order_history(user_id: int):
    """获取用户的完整订单历史（包含订单项）"""
    try:
        service = get_ecommerce_service()
        orders = service.get_user_order_history(user_id)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/orders/{order_id}/status", response_model=Dict[str, Any])
def update_order_status(order_id: int, request: UpdateOrderStatusRequest):
    """更新订单状态"""
    try:
        service = get_ecommerce_service()
        result = service.order_service.update_order_status(order_id, request.status)
        return {"message": "订单状态更新成功", "affected_rows": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int):
    """删除订单"""
    try:
        service = get_ecommerce_service()
        result = service.order_service.delete_order(order_id)
        if result == 0:
            raise HTTPException(status_code=404, detail="订单不存在")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 订单项相关API端点
# ============================================================================

@app.get("/orders/{order_id}/items", response_model=List[OrderItemResponse])
def get_order_items(order_id: int):
    """获取订单的所有商品项"""
    try:
        service = get_ecommerce_service()
        items = service.order_item_service.get_order_items(order_id)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/{order_id}/total", response_model=Dict[str, Any])
def get_order_total(order_id: int):
    """获取订单总金额"""
    try:
        service = get_ecommerce_service()
        total = service.order_item_service.get_order_total_amount(order_id)
        return {"order_id": order_id, "total_amount": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 健康检查端点
# ============================================================================

@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "E-Commerce API"}

@app.get("/")
def root():
    """根路径"""
    return {"message": "E-Commerce API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
