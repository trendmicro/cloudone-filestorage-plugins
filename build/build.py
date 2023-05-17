import os
import shutil

def clean_build_directory():
    build_dir = "build"
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)


def compile_source_code():
    print('compile source code')


def copy_assets():
    print('copy assets')


def create_release_zip():
    shutil.make_archive("release", "zip", "build")


def main():
    clean_build_directory()
    compile_source_code()
    copy_assets()
    create_release_zip()


if __name__ == "__main__":
    main()
