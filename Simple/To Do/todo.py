import argparse
import json
import os
import sys

DATA_FILE = 'todo.json'

def load_tasks():
  if not os.path.exists(DATA_FILE):
    return []
  with open(DATA_FILE, 'r') as f:
    return json.load(f)
  
def save_tasks(tasks):
  with open(DATA_FILE, 'w') as f:
    json.dump(tasks, f, indent=2)

def get_next_id(tasks):
  return max((t['id'] for t in tasks), default=0) + 1

def cmd_add(args):
  tasks = load_tasks()
  new = {
    'id': get_next_id(tasks),
    'description': args.description,
    'done': False
  }
  tasks.append(new)
  save_tasks(tasks)
  print(f"Added tasks {new['id']}: {new['description']}")

def cmd_list(args):
  tasks = load_tasks()
  if not tasks:
    print("No tasks yet.")
    return
  for t in tasks:
    status = '✓' if t['done'] else ' '
    print(f"[{status}] {t['id']:>3} {t['description']}")

def cmd_done(args):
  tasks = load_tasks()
  for t in tasks:
    if t['id'] == args.id:
      t['done'] = True
      save_tasks(tasks)
      print(f"Marked task {t['id']} done.")
      return
  print(f"No task with id {args.id}", file=sys.stderr)
  sys.exit(1)

def cmd_remove(args):
  tasks = load_tasks()
  filtered = [t for t in tasks if t['id'] != args.id]
  if len(filtered) == len(tasks):
    print(f"No task with id {args.id}", file=sys.stderr)
    sys.exit(1)
  save_tasks(filtered)
  print(f"Removed task {args.id}.")

def main():
  parser = argparse.ArgumentParser(prog='todo', description='Simple JSON-backed CLI to-do app')
  sub = parser.add_subparsers(dest='cmd')
  sub.required = True

  p = sub.add_parser('add', help='Add a new tasks')
  p.add_argument('description', nargs='+', help='Task description')
  p.set_defaults(func=cmd_add)

  p = sub.add_parser('list', help='List all tasks')
  p.set_defaults(func=cmd_list)

  p = sub.add_parser('done', help='Mark task done')
  p.add_argument('id', type=int, help='ID of task to mark done')
  p.set_defaults(func=cmd_done)

  p = sub.add_parser('remove', help='Remove a task')
  p.add_argument('id', type=int, help='ID of task to remove')
  p.set_defaults(func=cmd_remove)

  args = parser.parse_args()
  if hasattr(args, 'description') and isinstance(args.description, list):
    args.description = ' '.join(args.description)
  args.func(args)

if __name__ == '__main__':
  main()