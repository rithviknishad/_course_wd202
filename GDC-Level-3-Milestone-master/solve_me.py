from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as parse
import json


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

    def render_add_task(self):
        content = f"""
<div class="w-full max-w-xs">
  <form action="add" method="GET" class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4" id="add_task_form">
    <div class="mb-4">
      <label class="block text-gray-700 text-sm font-bold mb-2">
        Describe the task
      </label>
      <input name="task" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" type="text" placeholder="Task">
    </div>
    <div class="mb-6">
      <label class="block text-gray-700 text-sm font-bold mb-2">
        Priority
      </label>
      <input name="priority" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline" type="text" placeholder="Priority (1 being highest)">
    </div>
    <div class="flex items-center justify-between">
      <button 
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        type="submit"
        form="add_task_form"
        value="Add"
      >
        Add
      </button>
    </div>
  </form>
</div>
        """
        return self.render_page_from_template("Add new task", content)

    def render_pending_tasks(self):
        subcontent = "<h6>Hooray! You've no tasks pending!</h6>"
        if len(self.current_items) != 0:
            subcontent = "".join(
                [
                    self.render_pending_task_tile(*task)
                    for task in self.current_items.items()
                ]
            )
        content = f"""
        <div class="flex items-center justify-center py-6">
            <button class="relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-purple-600 to-blue-500 group-hover:from-purple-600 group-hover:to-blue-500 hover:text-white dark:text-white focus:ring-4 focus:ring-blue-300 dark:focus:ring-blue-800">
                <span class="relative px-5 py-2.5 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-opacity-0" onclick="location.href='/completed'">
                    Completed Tasks
                </span>
            </button>
            <button 
                type="button" 
                class="text-white bg-gradient-to-br from-purple-600 to-blue-500 hover:bg-gradient-to-bl focus:ring-4 focus:ring-blue-300 dark:focus:ring-blue-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2"
                onclick="location.href='/add'"
            >
                Add new task
            </button>
        </div>
        <div class="flex items-center justify-center py-6">
            <div class="grid xl:grid-cols-4 lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-4 text-slate-200">{subcontent}</div>
        </div>"""
        return self.render_page_from_template("Pending Tasks", content)

    def render_completed_tasks(self):
        subcontent = "<h6>You haven't completed any tasks yet :(</h6>"
        if len(self.completed_items) != 0:
            subcontent = "".join(
                [self.render_completed_task_tile(task) for task in self.completed_items]
            )
        content = f"""
        <div class="flex items-center justify-center py-6">
            <button class="relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-purple-600 to-blue-500 group-hover:from-purple-600 group-hover:to-blue-500 hover:text-white dark:text-white focus:ring-4 focus:ring-blue-300 dark:focus:ring-blue-800">
                <span class="relative px-5 py-2.5 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-opacity-0" onclick="location.href='/tasks'">
                    Pending Tasks
                </span>
            </button>
        </div>
        <div class="flex items-center justify-center py-6">
            <div class="grid grid-cols-1 gap-2 text-slate-200">{subcontent}</div>
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
<div class="flex justify-center">
  <div class="block p-6 rounded-lg shadow-lg bg-white max-w-sm">
    <h5 class="text-gray-900 text-xl leading-tight font-medium mb-2">{task}</h5>
    <p class="text-gray-700 text-base mb-4">
      Priority : {priority}
    </p>
    <button 
        type="button" 
        class="inline-block px-6 py-2.5 bg-blue-600 text-white font-medium text-xs leading-tight uppercase rounded shadow-md hover:bg-blue-700 hover:shadow-lg focus:bg-blue-700 focus:shadow-lg focus:outline-none focus:ring-0 active:bg-blue-800 active:shadow-lg transition duration-150 ease-in-out"
        onclick="location.href='/done?priority={priority}'"
    >
        Mark as done
    </button>
    <button
        type="button"
        class="inline-block px-6 py-2.5 bg-blue-600 text-white font-medium text-xs leading-tight uppercase rounded shadow-md hover:bg-blue-700 hover:shadow-lg focus:bg-blue-700 focus:shadow-lg focus:outline-none focus:ring-0 active:bg-blue-800 active:shadow-lg transition duration-150 ease-in-out"
        onclick="location.href='/delete?priority={priority}'"
    >
        Delete
    </button>
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

        # TODO: ignore reading from volume on every request.
        task_command_object.read_current()
        task_command_object.read_completed()

        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        elif self.path.startswith("/add"):
            params = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
            if {"task", "priority"} <= params.keys():
                task_command_object.run("add", [params["priority"], params["task"]])
                content = self.redirect_to("/tasks")
            else:
                content = task_command_object.render_add_task()
        elif self.path.startswith("/done"):
            params = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
            if {"priority"} <= params.keys():
                task_command_object.run("done", [params["priority"]])
            content = self.redirect_to("/tasks")
        elif self.path.startswith("/delete"):
            params = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
            if {"priority"} <= params.keys():
                task_command_object.run("delete", [params["priority"]])
            content = self.redirect_to("/tasks")
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def redirect_to(self, location):
        return f"""<script type="text/javascript">window.location.href = "{location}"</script>"""
