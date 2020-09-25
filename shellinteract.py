import subprocess
from queue import Queue
from threading import Thread


class InteractiveShell:
    def __init__(self, command, PS1, logfile):
        def _enqueue_output(out, queue, out_file):
            for line in iter(out.readline, b''):
                out_file.write(line)
                queue.put(line)
                out.close()

        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, shell=False, universal_newlines=True)
        self.outQueue = Queue()
        self.outThread = Thread(target=_enqueue_output, args=(self.process.stdout, self.outQueue, logfile))
        self.outThread.daemon = True
        self.outThread.start()
        self.PS1 = PS1

    def execute(self, command):
        self.process.stdin.write(command + '\n')

    def get_output(self):
        output = ''
        while self.PS1 not in output:
            self.outQueue.get()
        return output

    def execute_and_get_output(self, command):
        self.execute(command)
        return self.get_output()

    def stop(self, timeout=0.2):
        self.execute('exit')
        try:
            self.process.wait(timeout)
        except subprocess.TimeoutExpired:
            self.process.kill()
