import threading

from main import GuitarArpeggiator


class InteractiveCLI:
    """Keyboard-driven controller for GuitarArpeggiator.

    Start/stop runs in a background thread so you can adjust settings live.
    """

    def __init__(self):
        self.arpeggiator = GuitarArpeggiator()
        self.run_thread = None
        self.running = False

    def start(self):
        if self.running:
            print("Already running.")
            return
        self.running = True
        self.run_thread = threading.Thread(target=self.arpeggiator.start, daemon=True)
        self.run_thread.start()
        print("Started arpeggiator in background.")

    def stop(self):
        if not self.running:
            print("Not running.")
            return
        self.arpeggiator.stop()
        # Allow the start() loop to exit
        if self.run_thread:
            self.run_thread.join(timeout=2.0)
        self.run_thread = None
        self.running = False
        print("Stopped arpeggiator.")

    def status(self):
        print("\n=== Status ===")
        print(f"Running: {self.running}")
        print(f"Tempo: {self.arpeggiator.tempo} BPM")
        print(f"Pattern: {self.arpeggiator.pattern}")
        print(f"Synth: {self.arpeggiator.synth_type}")
        print(f"Duration: {self.arpeggiator.duration} s")
        current = getattr(self.arpeggiator, 'current_chord', None)
        if current and current.get('valid'):
            print(f"Current chord: {current.get('root')} {current.get('quality')} (conf {current.get('confidence'):.2f})")
        else:
            print("Current chord: none")
        print("==============\n")

    def list_patterns(self):
        patterns = list(self.arpeggiator.arpeggio_engine.patterns.keys())
        print("Available patterns:", ", ".join(patterns))

    def list_synths(self):
        synths = list(self.arpeggiator.synth_engine.synth_types.keys())
        print("Available synths:", ", ".join(synths))

    def print_help(self):
        print(
            """
Interactive commands:
  start                      Start the arpeggiator
  stop                       Stop the arpeggiator
  status                     Show current status

  tempo <bpm>                Set tempo (60-200)
  tempo +<n> | tempo -<n>    Adjust tempo by n (e.g., tempo +10)

  pattern <name>             Set pattern (type 'patterns' to list)
  synth <name>               Set synth (type 'synths' to list)
  duration <seconds>         Set arpeggio duration in seconds (0.5 - 10.0)

  demo                       Play demo C major arpeggio once
  test_audio                 Play a 440Hz test tone

  patterns                   List available patterns
  synths                     List available synths
  help | h | ?               Show this help
  quit | q | exit            Stop and exit
            """.strip()
        )

    def run(self):
        print("\n=== Guitar Arpeggiator - Interactive CLI ===")
        self.print_help()
        try:
            while True:
                try:
                    line = input("cli> ").strip()
                except EOFError:
                    line = "quit"

                if not line:
                    continue

                parts = line.split()
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd in ("quit", "q", "exit"):
                    break
                elif cmd == "help" or cmd in ("h", "?"):
                    self.print_help()
                elif cmd == "start":
                    self.start()
                elif cmd == "stop":
                    self.stop()
                elif cmd == "status":
                    self.status()
                elif cmd == "tempo":
                    if not args:
                        print("Usage: tempo <bpm>|+<n>|-<n>")
                        continue
                    val = args[0]
                    try:
                        if val.startswith("+") or val.startswith("-"):
                            delta = int(val)
                            self.arpeggiator.set_tempo(self.arpeggiator.tempo + delta)
                        else:
                            bpm = int(val)
                            self.arpeggiator.set_tempo(bpm)
                    except ValueError:
                        print("Invalid tempo value.")
                elif cmd == "pattern":
                    if not args:
                        print("Usage: pattern <name>")
                        self.list_patterns()
                        continue
                    self.arpeggiator.set_pattern(args[0])
                elif cmd == "synth":
                    if not args:
                        print("Usage: synth <name>")
                        self.list_synths()
                        continue
                    self.arpeggiator.set_synth(args[0])
                elif cmd == "duration":
                    if not args:
                        print("Usage: duration <seconds>")
                        continue
                    try:
                        seconds = float(args[0])
                        self.arpeggiator.set_duration(seconds)
                    except ValueError:
                        print("Invalid duration value.")
                elif cmd == "demo":
                    self.arpeggiator.demo_mode()
                elif cmd == "test_audio":
                    self.arpeggiator.test_audio_system()
                elif cmd == "patterns":
                    self.list_patterns()
                elif cmd == "synths":
                    self.list_synths()
                else:
                    print(f"Unknown command: {cmd}")
        except KeyboardInterrupt:
            print("\nInterrupted.")
        finally:
            # Ensure we stop audio threads
            if self.running:
                self.stop()
            print("Goodbye.")


def main():
    cli = InteractiveCLI()
    cli.run()


if __name__ == "__main__":
    main()


