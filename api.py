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

# ============================================================================
# 请求和响应模型
# ============================================================================

class UserCreateRequest(BaseModel):
    """创建用户请求"""
    username: str = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., description="密码")
    full_name: Optional[str] = Field(None, description="全名")
    phone: Optional[str] = Field(None, description="电话")

class UserUpdateRequest(BaseModel):
    """更新用户请求"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(BaseModel):
    """用户响应"""
    user_id: int
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    created_at: Optional[datetime] = None

class CategoryCreateRequest(BaseModel):
    """创建分类请求"""
    category_name: str = Field(..., description="分类名称")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    description: Optional[str] = Field(None, description="分类描述")

class CategoryUpdateRequest(BaseModel):
    """更新分类请求"""
    category_name: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    """分类响应"""
    category_id: int
    category_name: str
    parent_id: Optional[int]
    description: Optional[str]

class ProductCreateRequest(BaseModel):
    """创建商品请求"""
    product_name: str = Field(..., description="商品名称")
    price: float = Field(..., gt=0, description="价格")
    category_id: int = Field(..., description="分类ID")
    description: Optional[str] = Field(None, description="商品描述")
    stock_quantity: int = Field(0, ge=0, description="库存数量")

class ProductUpdateRequest(BaseModel):
    """更新商品请求"""
    product_name: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    description: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)

class ProductResponse(BaseModel):
    """商品响应"""
    product_id: int
    product_name: str
    description: Optional[str]
    price: float
    stock_quantity: int
    category_id: int
    category_name: Optional[str] = None

class OrderItemRequest(BaseModel):
    """订单项请求"""
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(..., gt=0, description="数量")
    unit_price: float = Field(..., gt=0, description="单价")

class OrderCreateRequest(BaseModel):
    """创建订单请求"""
    user_id: int = Field(..., description="用户ID")
    items: List[OrderItemRequest] = Field(..., description="订单项列表")
    shipping_address: str = Field(..., description="收货地址")

class OrderResponse(BaseModel):
    """订单响应"""
    order_id: int
    user_id: int
    total_amount: float
    status: str
    shipping_address: str
    order_date: Optional[datetime] = None
    username: Optional[str] = None
    full_name: Optional[str] = None

class OrderItemResponse(BaseModel):
    """订单项响应"""
    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: Optional[float] = None
    product_name: Optional[str] = None
    description: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    new_password: str = Field(..., min_length=6, description="新密码")

class SearchRequest(BaseModel):
    """搜索请求"""
    keyword: str = Field(..., description="搜索关键词")

class UpdateStockRequest(BaseModel):
    """更新库存请求"""
    stock_quantity: int = Field(..., ge=0, description="库存数量")

class UpdateOrderStatusRequest(BaseModel):
    """更新订单状态请求"""
    status: str = Field(..., description="订单状态")
