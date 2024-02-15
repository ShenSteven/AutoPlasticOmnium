C:
        cd C:\Windows\System32
        taskkill /f /t /im python.exe
        net use S: /del /y&net use S: \\10.177.4.201\python /USER:user\pwd
        echo D|xcopy S:\python D:\python /Y /s /e
        net use S: /del /y
        cd /D D:\python
        start python.exe
        exit
        