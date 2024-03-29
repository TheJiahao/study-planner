from tkinter import BooleanVar, IntVar, StringVar, TclError, constants, filedialog, ttk
from tkinter.messagebox import askyesno, showerror

from config import COURSE_NAME_WIDTH, PERIODS_PER_YEAR
from entities.course import Course
from services.import_service import FileCorruptedError
from services.planner_service import TimingError, planner_service
from ui.view import View


class CreateCourseView(View):
    """Kurssin luomisesta vastaava näkymä."""

    def __init__(
        self,
        root: ttk.Widget,
    ) -> None:
        """Luokan konstruktori.

        Args:
            root (ttk.Widget): Juurikomponentti näkymälle.
        """

        super().__init__(root)

        self.__name_variable: StringVar = StringVar(value="")
        self.__credits_variable: IntVar = IntVar(value=0)
        self.__course_variable: StringVar = StringVar(value="")
        self.__course_list: list[str] = []
        self.__timing_frame: ttk.Frame = ttk.Frame(master=self._frame)
        self.__timing: list[BooleanVar] = [
            BooleanVar(value=False) for i in range(PERIODS_PER_YEAR)
        ]

        self.__requirement_frame: ttk.Frame = ttk.Frame(master=self._frame)
        self.__requirements: list[StringVar] = []
        self.__current_id: int = -1

        self.__initialize()

    def __initialize(self) -> None:
        self.__update_course_list()

        self.__initialize_course_field()
        self.__initialize_name_field()
        self.__initialize_credits_field()
        self.__initialize_timing_field()
        self.__initialize_requirement_field()
        self.__initialize_buttons()

    def __initialize_buttons(self) -> None:
        save_button = ttk.Button(
            master=self._frame,
            text="Tallenna",
            command=self.__handle_save,
        )
        delete_button = ttk.Button(
            master=self._frame,
            text="Poista",
            command=self.__handle_delete,
        )
        clear_button = ttk.Button(
            master=self._frame,
            text="Tyhjennä",
            command=self.__handle_clear,
        )

        import_export_frame = ttk.Frame(master=self._frame)

        import_button = ttk.Button(
            master=import_export_frame,
            text="Tuo",
            command=self.__handle_import,
            width=3,
        )
        export_button = ttk.Button(
            master=import_export_frame,
            text="Vie",
            command=self.__handle_export,
            width=3,
        )

        save_button.grid(
            row=7, column=1, sticky=constants.W + constants.S, padx=10, pady=10
        )
        delete_button.grid(
            row=7, column=2, sticky=constants.E + constants.S, padx=10, pady=10
        )
        clear_button.grid(row=0, column=1, sticky=constants.NSEW, padx=10, pady=10)

        import_button.grid(row=1, column=1, padx=3)
        export_button.grid(row=1, column=2, padx=3)
        import_export_frame.grid(
            row=0, column=2, sticky=constants.N + constants.E, padx=10, pady=10
        )

    def __initialize_course_field(self) -> None:
        course_label = ttk.Label(master=self._frame, text="Selaa")

        course_dropdown_list = ttk.Combobox(
            master=self._frame,
            state="readonly",
            values=self.__course_list,
            textvariable=self.__course_variable,
            postcommand=lambda: course_dropdown_list.configure(
                values=self.__course_list
            ),
            width=COURSE_NAME_WIDTH,
        )
        course_dropdown_list.bind("<<ComboboxSelected>>", self.__fill_course_data)

        course_label.grid(row=1, column=1, sticky=constants.W, padx=10)
        course_dropdown_list.grid(row=1, column=2, sticky=constants.W, pady=2, padx=10)

    def __initialize_name_field(self) -> None:
        name_label = ttk.Label(master=self._frame, text="Nimi")

        name_entry = ttk.Entry(
            master=self._frame,
            textvariable=self.__name_variable,
            width=COURSE_NAME_WIDTH,
        )

        name_label.grid(row=2, column=1, sticky=constants.W, padx=10)
        name_entry.grid(
            row=2, column=2, columnspan=2, sticky=constants.W, pady=2, padx=10
        )

    def __initialize_credits_field(self) -> None:
        credits_label = ttk.Label(master=self._frame, text="Laajuus (op)")

        credits_spinbox = ttk.Spinbox(
            master=self._frame,
            from_=0,
            to=20,
            increment=1,
            width=3,
            textvariable=self.__credits_variable,
        )

        credits_label.grid(row=3, column=1, sticky=constants.W, padx=10)
        credits_spinbox.grid(row=3, column=2, sticky=constants.W, pady=2, padx=10)

    def __initialize_timing_field(self) -> None:
        timing_label = ttk.Label(master=self._frame, text="Ajoitus (periodit)")

        timing_label.grid(row=4, column=1, sticky=constants.W, padx=10)

        for i, period_variable in enumerate(self.__timing):
            button = ttk.Checkbutton(
                master=self.__timing_frame, text=str(i + 1), variable=period_variable
            )

            button.grid(row=1, column=i)

        self.__timing_frame.grid(row=4, column=2, sticky=constants.W, pady=2, padx=10)

    def __initialize_requirement_field(self) -> None:
        requirement_label = ttk.Label(master=self._frame, text="Esitietovaatimukset")

        add_requirement_button = ttk.Button(
            master=self._frame, text="+", command=self.__handle_add_requirement, width=2
        )

        add_requirement_button.grid(
            row=5, column=2, sticky=constants.E, padx=10, pady=2
        )
        requirement_label.grid(row=5, column=1, sticky=constants.W, padx=10)
        self.__requirement_frame.grid(
            row=6, column=1, columnspan=2, sticky=constants.E, pady=2, padx=10
        )

    def __fill_course_data(self, event) -> None:
        """Täyttää valitun kurssin tiedot."""

        course_str = self.__handle_clear()
        self.__course_variable.set(course_str)

        self.__current_id = self.__extract_id(self.__course_variable)
        course = planner_service.get_course(self.__current_id)

        if course is None:
            showerror("Virhe", "Valittua kurssia ei löydy!")
            return

        self.__name_variable.set(course.name)
        self.__credits_variable.set(course.credits)

        for period in course.timing:
            self.__timing[period - 1].set(True)

        for requirement_id in course.requirements:
            requirement = planner_service.get_course(requirement_id)
            self.__handle_add_requirement(requirement)

    def __handle_import(self) -> None:
        """Tuo käyttäjän määräämästä JSON-tiedostosta kurssit."""

        confirm = askyesno(
            "Tuo kurssit", "Kurssien tuonti poistaa jo olevat kurssit. Varmista tuonti."
        )

        if not confirm:
            return

        path = filedialog.askopenfilename(filetypes=[("JSON-tiedostot", "*.json")])

        if not path:
            return

        try:
            planner_service.import_courses(path)
        except FileCorruptedError as error:
            showerror("Virhe", str(error))
        except FileNotFoundError:
            showerror("Virhe", "Tiedostoa ei löytynyt.")

        self.__handle_clear()
        self.__update_course_list()

    def __handle_export(self) -> None:
        """Vie kurssit käyttäjän määräämään JSON-tiedostoon."""

        path = filedialog.asksaveasfilename(filetypes=[("JSON-tiedostot", "*.json")])

        if not path:
            return

        planner_service.export_courses(path)

    def __handle_clear(self) -> str:
        """Tyhjentää täytetyt tiedot."""

        selected_course = self.__course_variable.get()
        self.__course_variable.set("")
        self.__current_id = -1
        self.__name_variable.set("")
        self.__credits_variable.set(0)

        for period_variable in self.__timing:
            period_variable.set(False)

        self.__requirements.clear()

        for row in self.__requirement_frame.winfo_children():
            row.destroy()

        return selected_course

    def __handle_save(self) -> None:
        """Tallentaa kurssin tiedot."""

        name = self.__name_variable.get().strip()

        try:
            credits = self.__credits_variable.get()
        except TclError:
            showerror("Virhe", "Tarkista opintopistemäärä.")
            return

        timing = {
            i + 1
            for i, period_variable in enumerate(self.__timing)
            if period_variable.get()
        }

        try:
            requirements = {
                self.__extract_id(course_variable)
                for course_variable in self.__requirements
            }
        except ValueError:
            showerror("Virhe", "Tarkista esitietovaatimukset.")
            return

        try:
            course = Course(name, credits, timing, requirements, self.__current_id)

            planner_service.create_course(course)

            self.__course_variable.set("")
            self.__update_course_list()
            self.__handle_clear()
        except (TimingError, ValueError) as error:
            showerror("Virhe", str(error))

    def __handle_delete(self) -> None:
        """Poistaa kurssin, vaatii käyttäjältä varmistuksen."""

        confirm = askyesno("Poista kurssi", "Varmista poisto")

        if not confirm:
            return

        planner_service.delete_course(self.__current_id)

        self.__course_variable.set("")
        self.__update_course_list()
        self.__handle_clear()

    def __handle_add_requirement(self, course: Course | None = None) -> None:
        """Lisää esitietovaatimusrivin.

        Args:
            course (Course | None, optional): Esitiedoksi lisättävä kurssi. Oletukseltaan None.
        """

        requirement_variable = StringVar(value="")
        requirement_row = ttk.Frame(master=self.__requirement_frame)

        self.__requirements.append(requirement_variable)

        requirement_dropdown = ttk.Combobox(
            master=requirement_row,
            values=self.__course_list,
            textvariable=requirement_variable,
            state="readonly",
            width=COURSE_NAME_WIDTH,
        )

        delete_button = ttk.Button(
            master=requirement_row,
            text="-",
            command=lambda: self.__handle_remove_requirement(
                requirement_variable, requirement_row
            ),
            width=1,
        )

        if course:
            requirement_variable.set(str(course))

        delete_button.grid(row=1, column=1, sticky=constants.E, padx=5, pady=2)
        requirement_dropdown.grid(row=1, column=2, sticky=constants.E)
        requirement_row.grid(column=1, sticky=constants.E)

    def __handle_remove_requirement(self, variable: StringVar, row: ttk.Frame) -> None:
        """Poistaa esitietovaatimuksen.

        Args:
            variable (StringVar): Esitietokurssin merkkijonoesitystä tallentava muuttuja.
            row (ttk.Frame): Poistettava esitietorivi.
        """

        self.__requirements.remove(variable)
        row.destroy()

    def __extract_id(self, course_variable: StringVar) -> int:
        """Palauttaa kurssin id:n.

        Args:
            course_variable (StringVar): Kurssin merkkijonoesitystä tallentava muuttuja.

        Returns:
            int: Kurssin id.
        """
        return int(course_variable.get().split(":")[0])

    def __update_course_list(self) -> None:
        self.__course_list = [
            str(course) for course in planner_service.get_all_courses()
        ]
