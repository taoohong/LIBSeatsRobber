from secrets import choice
import schedule

if __name__ == '__main__':
    print('author: taosupr\n\nfunction: Used to order' +\
        ' a seat at the HuaiNing Library \n\nwarning: Propagation of this script is prohibited;\n\n' + \
        'This script is not intended for commercial use.\n')

    print("出现！！！！！！表示程序没有按预期进行，届时请分析具体原因\n\n")
    acc = input("请输入账号：")
    while acc == "" or acc == None:
        acc = input("请重新输入账号：")
    pwd = input("请输入密码：")
    while pwd == "" or pwd == None:
        pwd = input("请重新输入密码：")
    print("请选择补强还是预抢，并输入对应序号，如 1\n1 补抢\t\t2 预抢")
    c = input()
    while c!= "1" and c!= "2":
        print("请选择补强还是预抢，并输入对应序号，如 1\n1 补抢\t\t2 预抢")
        c = input()
    date = "today"
    if c == "2":
        date = "tomorrow"
    sc = schedule.Schedule(acc, pwd, date)
    sc.run()