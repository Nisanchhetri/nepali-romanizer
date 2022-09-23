import os
import glob

def rename(input_dir, format=''):
    """Rename all the files in input_dir"""

    # Check that the input_dir exists and format is not blank
    assert os.path.exists(input_dir)
    assert format != ''

    # files = glob.glob(os.path.join(input_dir, "*"+format))
    files = os.listdir(input_dir)
    for file in files:
        _, side = file.split('_')
        side, num = side.split(' ')
        num, format = num.split('.')
        num = num.split('-')[0]
        new_name = 'Eye{}{}.{}'.format(num,side,format)
        # print(new_name, num)
        os.rename(os.path.join(input_dir,file), os.path.join(input_dir,new_name))


if __name__ == "__main__":
    input_dir = "E:/Eye/F18"
    rename(input_dir=input_dir, format=".png")