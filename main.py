import gui.application_window as aw
import local_data.file_handler as fh


class PMET:
    def __init__(self, is_visual=True):
        self.file_handler = fh.FileHandler()
        self.application_window = aw.App(self.file_handler)

        self.is_visual = is_visual

    def start_window(self):
        self.application_window.mainloop()


def main():
    pmet = PMET()

    if pmet.is_visual:
        pmet.start_window()


if __name__ == "__main__":
    main()
