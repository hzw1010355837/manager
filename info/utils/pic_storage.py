import qiniu

access_key = "hPZDiDGgMxgXuhes1gtvID1JKx_COF9PpI8GdqWF"
secret_key = "8ypQcQ7pnmp6FYSQ5coDC0FkXeX0Q27k8FVchFUN"
bucket_name = "information"


# TODO 没带身份证下午做
def pic_storage(data):
    q = qiniu.Auth(access_key, secret_key)
    # key = 'hello'
    # data = 'hello qiniu!'
    token = q.upload_token(bucket_name)
    ret, info = qiniu.put_data(token, None, data)
    if ret is not None:
        print('All is OK')
    else:
        print(info)  # error message in info
