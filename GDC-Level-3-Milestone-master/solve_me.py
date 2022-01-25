from http.server import BaseHTTPRequestHandler, HTTPServer

from matplotlib.pyplot import title


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = file.readlines()
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args, flush=True):
        priority = int(args[0])
        task = " ".join(args[1:])
        if priority in self.current_items.keys():
            self.add([priority + 1, self.current_items.pop(priority)], flush=False)
        self.current_items[priority] = task
        if flush:
            self.write_current()
            print(f'Added task: "{task}" with priority {priority}')

    def done(self, args):
        priority = int(args[0])
        item = self.current_items.pop(priority, None)
        if item:
            self.completed_items.append(item)
            self.write_current()
            self.write_completed()
            print("Marked item as done.")
        else:
            print(f"Error: no incomplete item with priority {priority} exists.")

    def delete(self, args):
        priority = int(args[0])
        if self.current_items.pop(priority, None):
            self.write_current()
            print(f"Deleted item with priority {priority}")
        else:
            print(
                f"Error: item with priority {priority} does not exist. Nothing deleted."
            )

    def ls(self):
        self.current_items = dict(sorted(self.current_items.items()))
        for index, (priority, item) in enumerate(self.current_items.items()):
            print(f"{index + 1}. {item} [{priority}]")

    def report(self):
        print(f"Pending : {len(self.current_items)}")
        self.ls()
        print()
        print(f"Completed : {len(self.completed_items)}")
        for index, item in enumerate(self.completed_items):
            print(f"{index + 1}. {item}")

    def render_pending_tasks(self):
        content = f"""
        <div class="flex items-center justify-center py-6">
            <div class="grid grid-cols-1 gap-2">
                {"".join([self.render_pending_task_tile(*task) for task in self.current_items.items()])}
            </div>
        </div>"""
        return self.render_page_from_template("Pending Tasks", content)

    def render_completed_tasks(self):
        content = f"""
        <div class="flex items-center justify-center py-6">
            <div class="grid grid-cols-1 gap-2">
                {"".join([self.render_completed_task_tile(task) for task in self.completed_items])}
            </div>
        </div>"""
        return self.render_page_from_template("Completed Tasks", content)

    def render_page_from_template(self, page_title, content):
        return f"""
        <html>
            <head>
                <script src="https://cdn.tailwindcss.com"></script>
                <title>{page_title}</title>
            </head>
            <body class="font-mono bg-gradient-to-r from-[#080c11] to-[#0F172A]">
                <div class="md:container md:mx-auto px-6 py-10">
                    <div class="flex items-center justify-center screen py-6">
                        <h2 class="inline-block text-2xl sm:text-3xl font-medium text-slate-200 tracking-tight py-3">
                            {page_title}
                        </h2>
                    </div>
                    {content}
                </div>
            </body>
        </html>
        """

    def render_pending_task_tile(self, priority, task):
        return f"""
        <div class="flex w-full items-center flex justify-center items-center">
            <div>
                <div class="max-w-xs flex flex-col justify-between bg-gradient-to-br from-purple-600 to-blue-500 hover:from-pink-500 hover:to-yellow-500 rounded-lg mb-6 py-5 px-4">
                    <div>
                        <h4 class="focus:outline-none text-gray-100 font-bold mb-3">{task}</h4>
                        <p class="focus:outline-none text-gray-100 text-sm">Priority: {priority}</p>
                    </div>
                    <div>
                        <div class="flex items-center justify-between text-gray-800">
                            Add Delete / Mark as Done buttons
                        </div>
                    </div>
                </div>
            </div>
        </div>"""

    def render_completed_task_tile(self, task_description):
        return f"""
        <div class="text-white bg-green-700 hover:bg-green-800 focus:ring-4 focus:ring-green-300 font-medium rounded-full text-sm px-5 py-2.5 text-center mr-2 mb-2 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800">
            {task_description}
        </div>"""


class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()

        task_command_object.read_current()
        task_command_object.read_completed()

        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
