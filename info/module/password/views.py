from info.lib.yuntongxun.sms import CCP
from info.models import User
from info.utils.response_code import RET
from . import passport_bp
from flask import request, current_app, abort, make_response, jsonify
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


@passport_bp.route("/sms_code", methods=["POST"])
def send_smscode():
    """
    1获取参数
        获取三个参数:image_code_id,mobile,image_code
    2校验参数
    3逻辑处理
    4返回值
    """
    # request.data
    # 1获取参数
    param_dict = request.json
    mobile = param_dict["mobile"]
    image_code = param_dict["image_code"]
    image_code_id = param_dict["image_code_id"]
    # 2校验参数
    if not all([mobile, image_code, image_code_id]):
        current_app.logger.error("参数错误")
        # return jsonify({"errno": RET.PARAMERR, "errmsg": "参数错误"})
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    import re
    # print(1)
    if not re.match(r"1[3578][0-9]{9}", mobile):
        current_app.logger.error("手机号格式错误")
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")
    # 3比对参数
    # 真实值对比,并删除redis中真实值
    try:
        real_image_id = redis_store.get("Image_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="真实值异常")
    if real_image_id:
        try:
            redis_store.delete("Image_%s" % image_code_id)
        except Exception as e:
            current_app.logger.error("删除真实值错误")
            return jsonify(errno=RET.DBERR, errmsg="真实值异常")
    else:
        current_app.logger.error("删除真实值异常")
        return jsonify(errno=RET.DBERR, errmsg="删除真实值异常")
    # 细节1,大小写2,redis取出的值需要解码,bytes类型
    if real_image_id.lower() != image_code.lower():
        current_app.logger.error("传入的值与图片不符")
        return jsonify(errno=RET.NODATA, errmsg="传入的值与图片不符")

    # 4相等,发送短信
    try:
        User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="用户已存在")
    # 生成6位验证码
    import random
    sms_code = random.randint(0, 999999)
    sms_code = "%06d" % sms_code

    # 调用ccp发送短信
    """
    参数1： 手机号码
    参数2； {6位的短信验证码值，分钟}
    参数3： 模板id 1：您的验证码为{1}，请于{2}内正确输入，如非本人操作，请忽略此短信。
    """
    try:
        result = CCP().send_template_sms(mobile, {constants.SMS_CODE_REDIS_EXPIRES / 60, sms_code}, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="短信验证码失败")
    if result == -1:
        current_app.logger.error("短信验证码失败")
        return jsonify(errno=RET.DATAEXIST, errmsg="短信验证码失败")
    print(sms_code)
    # 发送短信验证码成功,保存6位的随机短信值到redis数据库
    try:
        redis_store.setex("SMS_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码异常")
    # finally
    return jsonify(errno=RET.OK, errmsg="发送短信验证码成功")
    return response