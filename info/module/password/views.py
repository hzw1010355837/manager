from . import passport_bp
from flask import request, current_app, abort,make_response
from info.utils.captcha.captcha import captcha
from info import redis_store,constants


# 127.0.0.1:5000/passport/image_code?code_id=UUID
@passport_bp.route('/image_code')
def get_image_code():
    """
    1,获取参数
        1.1获取code_id值
    2,校验参数
        2.1判断code_id是否有值
    3,逻辑处理
        3.1  生成验证码图片 & 生成验证码图片上的真实值
        3.2 根据code_id编号作为key将生成验证码图片上的真实值存储到redis数据，并且设置有效时长（后续接口需要校验）
    4,返回值
    """
    # 1, 获取参数
    code_id = request.args.get("code_id")
    # 2, 校验参数
    if not code_id:
        current_app.logger.error("参数不足")
        abort(403)
    # 3,逻辑处理
    image_name, image_code, image_data = captcha.generate_captcha()
    try:
        redis_store.setex("Image_%s" % code_id, constants.IMAGE_CODE_REDIS_EXPIRES, image_code)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    # 4,返回值
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/JPEG"
    return response