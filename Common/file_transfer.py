import ftplib
import os


class FTPUtils:
    def __init__(self, server, username, password):
        self.ftp = ftplib.FTP(server)
        self.ftp.login(username, password)
        self.download_buffer = 1024
        self.upload_buffer = 1024

    def change_dir(self, work_dir):
        return self.ftp.cwd(work_dir)

    def get_working_dir(self):
        return self.ftp.pwd()

    def get_item_list(self, work_dir):
        self.ftp.cwd(work_dir)
        return self.ftp.nlst()

    def is_item_file(self, item):
        try:
            self.ftp.cwd(item)
            self.ftp.cwd('..')
            return False
        except ftplib.error_perm as fe:
            if not fe.args[0].startswith('550'):
                raise
            return True

    def download_file(self, file_name, save_as_name):
        file_handler = open(save_as_name, 'wb')
        self.ftp.retrbinary("RETR " + file_name, file_handler.write, self.download_buffer)
        file_handler.close()
        return save_as_name

    def download_dir(self, dir_name, save_as_dir):
        if not os.path.exists(save_as_dir):
            os.mkdir(save_as_dir)
        self.ftp.cwd(dir_name)
        for item in self.ftp.nlst():
            if self.is_item_file(item):
                self.download_file(item, os.path.join(save_as_dir, item))
            else:
                self.download_dir(item, os.path.join(save_as_dir, item))
        self.ftp.cwd("..")
        return save_as_dir

    def upload_file(self, file_name, save_as_name):
        try:
            self.ftp.storbinary('STOR ' + save_as_name, open(file_name, 'rb'), self.upload_buffer)
            return save_as_name
        except Exception as e:
            print('Exception occurred when uploading file to FTP server path {}. Exception as below: \n\
            {}'.format(save_as_name, e))

    def new_dir(self, dir_name):
        try:
            self.ftp.mkd(dir_name)
        # ignore "directory already exists"
        except ftplib.error_perm as fe:
            if not fe.args[0].startswith('550'):
                raise
            return False
        return dir_name

    def upload_dir(self, dir_path, save_as_dir):
        try:
            self.ftp.cwd(save_as_dir)
        except ftplib.error_perm as fe:
            if fe.args[0].startswith('550'):
                self.new_dir(save_as_dir)
                self.ftp.cwd(save_as_dir)
        for item_name in os.listdir(dir_path):
            local_path = os.path.join(dir_path, item_name)
            if os.path.isfile(local_path):
                self.ftp.storbinary('STOR ' + item_name, open(local_path, 'rb'), self.upload_buffer)
            elif os.path.isdir(local_path):
                ftp_folder = self.new_dir(item_name)
                self.upload_dir(local_path, ftp_folder)
                self.ftp.cwd("..")
        return save_as_dir

    def delete_file(self, file_name):
        self.ftp.delete(file_name)
        return file_name

    def delete_dir(self, dir_name):
        # Handle dir_name doesn't exist
        try:
            self.change_dir(dir_name)
            items = self.ftp.nlst()
        except ftplib.all_errors as e:
            print(e)
            return
        for item in items:
            if os.path.split(item)[1] in ('.', '..'):
                continue
            try:
                self.change_dir(item)
                self.change_dir('../../../../..')
                self.delete_dir(item)
            except ftplib.all_errors:
                self.delete_file(item)
        try:
            self.change_dir('../../../../..')
            self.ftp.rmd(dir_name)
        except ftplib.all_errors as e:
            print(e)
        return dir_name

    def close(self):
        self.ftp.close()


if __name__ == '__main__':
    ftp = FTPUtils(r"15.83.255.102", r"administrator", "Shanghai2010")
    # ftp.download_file(r"ZC_TEST/testpath3.exe","testpath3.exe")
    ftp.upload_file(r"../Test_Report/Site1.yaml", "test/Test_Report/Site1.yaml")
