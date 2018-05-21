import os
import redis
import pymongo
import pymysql
import hashlib


def get_redis(host='localhost', port=6379, db=0, password=None):
    return redis.StrictRedis(host=host, port=port, db=db, password=password)


def get_mongodb(db_name, host='localhost', port=27017, username=None, password=None, is_admin=False):
    client = pymongo.MongoClient(host=host, port=port)
    database = client.get_database(db_name)
    database.authenticate(name=username, password=password) if username else None
    if is_admin:
        return client
    return database


def get_mysql(host='localhost', port=3306, username=None, password=None, db=None):
    if username is None or password is None or db is None:
        raise AttributeError('username, password and db can\'t be None!')
    return pymysql.connect(host=host, port=port, user=username, passwd=password, db=db)


def split_file_by_lines(file_path, otp_dir, row_cnt):
    def mk_sub_file(lines, head_, src_path, sub):
        file_full_name = os.path.basename(src_path)
        file_base_name, ext_name = os.path.splitext(file_full_name)
        sub_file_name = file_base_name + '_' + str(sub).zfill(5) + ext_name
        sub_file_path = os.path.join(otp_dir, sub_file_name)
        print(f'make file: {sub_file_path}')
        file_out = open(sub_file_path, 'w', encoding='utf-8')
        try:
            file_out.writelines([head_])
            file_out.writelines(lines)
            return sub + 1
        finally:
            file_out.close()

    file_src = open(file_path, 'r', encoding='utf-8')
    try:
        head = file_src.readline()
        buf = []
        sub = 1
        for line in file_src:
            buf.append(line)
            if len(buf) == row_cnt:
                sub = mk_sub_file(buf, head, file_path, sub)
                buf = []
        if len(buf) != 0:
            sub = mk_sub_file(buf, head, file_path, sub)
    finally:
        file_src.close()


# 返回目录下所有文件的绝对路径（包含文件夹，不包含子目录）
def get_files(dir_path):
    file_list = list()
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        file_list.append(file_path)
    return file_list


def is_chinese_character(character):
    x, y = ['\u4e00', '\u9fa5']
    return x <= character <= y


def md5(string):
    md5_str = hashlib.md5(string.encode('utf-8'))
    return md5_str.hexdigest()


def image_to_tiff(src_path, des_path):
    from libtiff import TIFF
    image = Image.open(src_path)
    image = image.convert('L')
    tiff_out = TIFF.open(des_path, 'w')
    tiff_out.write_image(image, compression=None, write_rgb=True)
    tiff_out.close()
