import sqlite3
from datetime import datetime, timedelta

def create_connection():
    """데이터베이스 연결을 생성하고 연결 객체를 반환합니다."""
    try:
        conn = sqlite3.connect('revi.db')
        return conn
    except sqlite3.Error as e:
        print(f"데이터베이스 연결 실패: {e}")
        return None

def create_table(conn):
    """데이터베이스에 tasks 테이블을 생성합니다."""
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tasks
                     (date TEXT, name TEXT, completed INTEGER DEFAULT 0)''')
    except sqlite3.Error as e:
        print(f"테이블 생성 실패: {e}")

def insert_task(conn, date, name):
    """새로운 작업을 tasks 테이블에 삽입합니다."""
    try:
        sql = ''' INSERT INTO tasks(date, name)
                  VALUES(?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (date, name))
        conn.commit()
        return cur.lastrowid
    except sqlite3.Error as e:
        print(f"작업 삽입 실패: {e}")
        return None

def get_tasks_by_date(conn, date):
    """특정 날짜의 작업 정보를 조회합니다."""
    try:
        cur = conn.cursor()
        cur.execute("SELECT rowid, date, name, completed FROM tasks WHERE date = ?", (date,))
        return cur.fetchall()
    except sqlite3.Error as e:
        print(f"작업 조회 실패: {e}")
        return []

def view(conn):
    """오늘 날짜에 해당하는 tasks의 모든 작업을 조회하고 번호순으로 출력합니다."""
    today = datetime.now().strftime("%Y-%m-%d")
    today_tasks = get_tasks_by_date(conn, today)

    print(f"\n오늘 날짜 ({today})의 작업 목록\n")
    for idx, (task_id, date, name, completed) in enumerate(today_tasks, start=1):
        status = "완료" if completed else "미완료"
        print(f"{idx}. {name} - {status}")

def get_future_dates(start_date, weeks):
    """주어진 시작 날짜로부터 특정 주 후의 날짜들을 반환합니다."""
    return [start_date + timedelta(weeks=w) for w in weeks]

def save(conn):
    """새로운 작업 정보를 입력받아 데이터베이스에 저장합니다."""
    task_names = input("한 일을 ,를 기준으로 주세요!: ").strip().split(",")
    now = datetime.now()
    future_weeks = [0, 1/7, 3/7, 1, 2, 4, 8, 16]  # 오늘, 1일 후, 3일 후, 1주 후, 2주 후, 4주 후, 8주 후, 16주 후
    future_dates = get_future_dates(now, future_weeks)

    task_ids = []
    for name in task_names:
        for date in future_dates:
            task_id = insert_task(conn, date.strftime("%Y-%m-%d"), name.strip())
            if task_id:
                task_ids.append(task_id)

    print("\n저장된 작업 목록:")
    for num, task in enumerate(task_names, start=1):
        print(f"{num}. {task}")

    return task_ids

def check(conn, task_ids):
    completed_tasks = input("\n어떤 할 일을 완료했나요? (번호를 ,로 구분하여 입력, 없으면 'n' 입력): ")
    if completed_tasks != 'n':
        for task_num in completed_tasks.split(","):
            try:
                task_id = task_ids[int(task_num) - 1]
                cur = conn.cursor()
                cur.execute("UPDATE tasks SET completed = 1 WHERE rowid = ?", (task_id,))
                conn.commit()
            except (IndexError, ValueError):
                print(f"잘못된 번호: {task_num}")
    else:
        print("\n^^7")

def select():
    """사용자 입력에 따라 다른 함수를 실행합니다."""
    conn = create_connection()
    if conn is None:
        return

    create_table(conn)

    while True:
        print("\n1. 작업 조회")
        print("2. 작업 저장")
        print("3. 작업 완료 체크")
        print("4. 종료")
        choice = input("선택: ")

        if choice == '1':
            view(conn)
        elif choice == '2':
            save(conn)
        elif choice == '3':
            today = datetime.now().strftime("%Y-%m-%d")
            today_tasks = get_tasks_by_date(conn, today)
            if not today_tasks:
                print("오늘의 작업이 없습니다.")
            else:
                task_ids = [task[0] for task in today_tasks]
                check(conn, task_ids)
        elif choice == "4":
            break
        else:
            print("잘못된 선택입니다. 다시 시도하세요.")

    conn.close()

def main():
    select()

if __name__ == '__main__':
    main()
