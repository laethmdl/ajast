from cx_Freeze import setup, Executable

setup(
    name="a",
    version="1.0",
    description="برنامج تحويل TXT إلى Excel",
    executables=[Executable("a.py", base="Win32GUI")]  # استخدم "Win32GUI" للتطبيقات الرسومية
)