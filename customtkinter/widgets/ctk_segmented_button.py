import tkinter
from typing import Union, Tuple, List, Dict, Callable

from ..theme_manager import ThemeManager
from .ctk_button import CTkButton
from .ctk_frame import CTkFrame


class CTkSegmentedButton(CTkFrame):
    """
    Segmented button with corner radius, border width, variable support.
    For detailed information check out the documentation.
    """

    def __init__(self,
                 master: any = None,
                 width: int = 140,
                 height: int = 28,
                 corner_radius: Union[int, str] = "default_theme",
                 border_width: Union[int, str] = 3,

                 bg_color: Union[str, Tuple[str, str], None] = None,
                 fg_color: Union[str, Tuple[str, str], None] = "default_theme",
                 selected_color: Union[str, Tuple[str, str]] = "default_theme",
                 selected_hover_color: Union[str, Tuple[str, str]] = "default_theme",
                 unselected_color: Union[str, Tuple[str, str]] = "default_theme",
                 unselected_hover_color: Union[str, Tuple[str, str]] = "default_theme",
                 text_color: Union[str, Tuple[str, str]] = "default_theme",
                 text_color_disabled: Union[str, Tuple[str, str]] = "default_theme",
                 background_corner_colors: Tuple[Union[str, Tuple[str, str]]] = None,

                 font: any = "default_theme",
                 values: list = None,
                 variable: tkinter.Variable = None,
                 dynamic_resizing: bool = True,
                 command: Callable[[str], None] = None,
                 state: str = "normal",
                 **kwargs):

        super().__init__(master=master, bg_color=bg_color, width=width, height=height, **kwargs)

        self._sb_fg_color = ThemeManager.theme["color"]["segmented_button"] if fg_color == "default_theme" else fg_color

        self._sb_selected_color = ThemeManager.theme["color"]["button"] if selected_color == "default_theme" else selected_color
        self._sb_selected_hover_color = ThemeManager.theme["color"]["button_hover"] if selected_hover_color == "default_theme" else selected_hover_color

        self._sb_unselected_color = ThemeManager.theme["color"]["segmented_button_unselected"] if unselected_color == "default_theme" else unselected_color
        self._sb_unselected_hover_color = ThemeManager.theme["color"]["segmented_button_unselected_hover"] if unselected_hover_color == "default_theme" else unselected_hover_color

        self._sb_text_color = ThemeManager.theme["color"]["text_button"] if text_color == "default_theme" else text_color
        self._sb_text_color_disabled = ThemeManager.theme["color"]["text_button_disabled"] if text_color_disabled == "default_theme" else text_color_disabled

        self._sb_corner_radius = ThemeManager.theme["shape"]["button_corner_radius"] if corner_radius == "default_theme" else corner_radius
        self._sb_border_width = ThemeManager.theme["shape"]["button_border_width"] if border_width == "default_theme" else border_width

        self._background_corner_colors = background_corner_colors  # rendering options for DrawEngine

        self._command: Callable[[str], None] = command
        self._font = (ThemeManager.theme["text"]["font"], ThemeManager.theme["text"]["size"]) if font == "default_theme" else font
        self._state = state

        self._buttons_dict: Dict[str, CTkButton] = {}  # mapped from value to button object
        if values is None:
            self._value_list: List[str] = ["CTkSegmentedButton"]
        else:
            self._value_list: List[str] = values  # Values ordered like buttons rendered on widget

        self._dynamic_resizing = dynamic_resizing
        if not self._dynamic_resizing:
            self.grid_propagate(False)

        self._check_unique_values(self._value_list)
        self._current_value: str = ""
        if len(self._value_list) > 0:
            self._create_buttons_from_values()
            self._create_button_grid()

        self._variable = variable
        self._variable_callback_blocked: bool = False
        self._variable_callback_name: Union[str, None] = None

        if self._variable is not None:
            self._variable_callback_name = self._variable.trace_add("write", self._variable_callback)
            self.set(self._variable.get(), from_variable_callback=True)

        super().configure(corner_radius=self._sb_corner_radius, fg_color=None)

    def destroy(self):
        if self._variable is not None:  # remove old callback
            self._variable.trace_remove("write", self._variable_callback_name)

        super().destroy()

    def _set_dimensions(self, width: int = None, height: int = None):
        super()._set_dimensions(width, height)

        for button in self._buttons_dict.values():
            button.configure(height=height)

    def _variable_callback(self, var_name, index, mode):
        if not self._variable_callback_blocked:
            self.set(self._variable.get(), from_variable_callback=True)

    def _get_index_by_value(self, value: str):
        for index, value_from_list in enumerate(self._value_list):
            if value_from_list == value:
                return index

        raise ValueError(f"CTkSegmentedButton does not contain value '{value}'")

    def _configure_button_corners_for_index(self, index: int):
        if index == 0 and len(self._value_list) == 1:
            if self._background_corner_colors is None:
                self._buttons_dict[self._value_list[index]].configure(background_corner_colors=(self._bg_color, self._bg_color, self._bg_color, self._bg_color))
            else:
                self._buttons_dict[self._value_list[index]].configure(background_corner_colors=self._background_corner_colors)

        elif index == 0:
            if self._background_corner_colors is None:
                self._buttons_dict[self._value_list[index]].configure(background_corner_colors=(self._bg_color, self._sb_fg_color, self._sb_fg_color, self._bg_color))
            else:
                self._buttons_dict[self._value_list[index]].configure(background_corner_colors=(self._background_corner_colors[0], self._sb_fg_color, self._sb_fg_color, self._background_corner_colors[3]))

        elif index == len(self._value_list) - 1:
            if self._background_corner_colors is None:
                self._buttons_dict[self._value_list[index]].configure(background_corner_colors=(self._sb_fg_color, self._bg_color, self._bg_color, self._sb_fg_color))
            else:
                self._buttons_dict[self._value_list[index]].configure(background_corner_colors=(self._sb_fg_color, self._background_corner_colors[1], self._background_corner_colors[2], self._sb_fg_color))

        else:
            self._buttons_dict[self._value_list[index]].configure(background_corner_colors=(self._sb_fg_color, self._sb_fg_color, self._sb_fg_color, self._sb_fg_color))

    def _unselect_button_by_value(self, value: str):
        if value in self._buttons_dict:
            self._buttons_dict[value].configure(fg_color=self._sb_unselected_color,
                                                hover_color=self._sb_unselected_hover_color)

    def _select_button_by_value(self, value: str):
        if self._current_value is not None and self._current_value != "":
            self._unselect_button_by_value(self._current_value)

        self._current_value = value

        self._buttons_dict[value].configure(fg_color=self._sb_selected_color,
                                            hover_color=self._sb_selected_hover_color)

    def _create_button(self, index: int, value: str) -> CTkButton:
        new_button = CTkButton(self,
                               height=self._current_height,
                               width=0,
                               corner_radius=self._sb_corner_radius,
                               text=value,
                               border_width=self._sb_border_width,
                               border_color=self._sb_fg_color,
                               fg_color=self._sb_unselected_color,
                               hover_color=self._sb_unselected_hover_color,
                               text_color=self._sb_text_color,
                               text_color_disabled=self._sb_text_color_disabled,
                               font=self._font,
                               state=self._state,
                               command=lambda v=value: self.set(v, from_button_callback=True),
                               background_corner_colors=None,
                               round_width_to_even_numbers=False)  # DrawEngine rendering option (so that theres no gap between buttons)

        return new_button

    @staticmethod
    def _check_unique_values(values: List[str]):
        """ raises exception if values are not unique """
        if len(values) != len(set(values)):
            raise ValueError("CTkSegmentedButton values are not unique")

    def _create_button_grid(self):
        # remove minsize from every grid cell in the first row
        number_of_columns, _ = self.grid_size()
        for n in range(number_of_columns):
            self.grid_columnconfigure(n, weight=1, minsize=0)
        self.grid_rowconfigure(0, weight=1)

        for index, value in enumerate(self._value_list):
            self.grid_columnconfigure(index, weight=1, minsize=self._current_height)
            self._buttons_dict[value].grid(row=0, column=index, sticky="ew")

    def _create_buttons_from_values(self):
        assert len(self._buttons_dict) == 0
        assert len(self._value_list) > 0

        for index, value in enumerate(self._value_list):
            self._buttons_dict[value] = self._create_button(index, value)
            self._configure_button_corners_for_index(index)

    def configure(self, **kwargs):
        if "bg_color" in kwargs:
            super().configure(bg_color=kwargs.pop("bg_color"))

            if len(self._buttons_dict) > 0:
                self._configure_button_corners_for_index(0)
            if len(self._buttons_dict) > 1:
                max_index = len(self._buttons_dict) - 1
                self._configure_button_corners_for_index(max_index)

        if "fg_color" in kwargs:
            self._sb_fg_color = kwargs.pop("fg_color")
            for index, button in enumerate(self._buttons_dict.values()):
                button.configure(border_color=self._sb_fg_color)
                self._configure_button_corners_for_index(index)

        if "selected_color" in kwargs:
            self._sb_selected_color = kwargs.pop("selected_color")
            if self._current_value in self._buttons_dict:
                self._buttons_dict[self._current_value].configure(fg_color=self._sb_selected_color)

        if "selected_hover_color" in kwargs:
            self._sb_selected_hover_color = kwargs.pop("selected_hover_color")
            if self._current_value in self._buttons_dict:
                self._buttons_dict[self._current_value].configure(hover_color=self._sb_selected_hover_color)

        if "unselected_color" in kwargs:
            self._sb_unselected_color = kwargs.pop("unselected_color")
            for value, button in self._buttons_dict.items():
                if value != self._current_value:
                    button.configure(fg_color=self._sb_unselected_color)

        if "unselected_hover_color" in kwargs:
            self._sb_unselected_hover_color = kwargs.pop("unselected_hover_color")
            for value, button in self._buttons_dict.items():
                if value != self._current_value:
                    button.configure(hover_color=self._sb_unselected_hover_color)

        if "text_color" in kwargs:
            self._sb_text_color = kwargs.pop("text_color")
            for button in self._buttons_dict.values():
                button.configure(text_color=self._sb_text_color)

        if "text_color_disabled" in kwargs:
            self._sb_text_color_disabled = kwargs.pop("text_color_disabled")
            for button in self._buttons_dict.values():
                button.configure(text_color_disabled=self._sb_text_color_disabled)

        if "background_corner_colors" in kwargs:
            self._background_corner_colors = kwargs.pop("background_corner_colors")
            for i in range(len(self._buttons_dict)):
                self._configure_button_corners_for_index(i)

        if "font" in kwargs:
            self._font = kwargs.pop("font")
            for button in self._buttons_dict.values():
                button.configure(font=self._font)

        if "values" in kwargs:
            for button in self._buttons_dict.values():
                button.destroy()
            self._buttons_dict.clear()
            self._value_list = kwargs.pop("values")

            self._check_unique_values(self._value_list)

            if len(self._value_list) > 0:
                self._create_buttons_from_values()
                self._create_button_grid()

            if self._current_value in self._value_list:
                self._select_button_by_value(self._current_value)

        if "variable" in kwargs:
            if self._variable is not None:  # remove old callback
                self._variable.trace_remove("write", self._variable_callback_name)

            self._variable = kwargs.pop("variable")

            if self._variable is not None and self._variable != "":
                self._variable_callback_name = self._variable.trace_add("write", self._variable_callback)
                self.set(self._variable.get(), from_variable_callback=True)
            else:
                self._variable = None

        if "dynamic_resizing" in kwargs:
            self._dynamic_resizing = kwargs.pop("dynamic_resizing")
            if not self._dynamic_resizing:
                self.grid_propagate(False)
            else:
                self.grid_propagate(True)

        if "command" in kwargs:
            self._command = kwargs.pop("command")

        if "state" in kwargs:
            self._state = kwargs.pop("state")
            for button in self._buttons_dict.values():
                button.configure(state=self._state)

        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "corner_radius":
            return self._sb_corner_radius
        elif attribute_name == "border_width":
            return self._sb_border_width

        elif attribute_name == "fg_color":
            return self._sb_fg_color
        elif attribute_name == "selected_color":
            return self._sb_selected_color
        elif attribute_name == "selected_hover_color":
            return self._sb_selected_hover_color
        elif attribute_name == "unselected_color":
            return self._sb_unselected_color
        elif attribute_name == "unselected_hover_color":
            return self._sb_unselected_hover_color
        elif attribute_name == "text_color":
            return self._sb_text_color
        elif attribute_name == "text_color_disabled":
            return self._sb_text_color_disabled

        elif attribute_name == "font":
            return self._font
        elif attribute_name == "values":
            return self._value_list
        elif attribute_name == "variable":
            return self._variable
        elif attribute_name == "dynamic_resizing":
            return self._dynamic_resizing
        elif attribute_name == "command":
            return self._command

        else:
            return super().cget(attribute_name)

    def set(self, value: str, from_variable_callback: bool = False, from_button_callback: bool = False):
        if value == self._current_value:
            return
        elif value in self._buttons_dict:
            self._select_button_by_value(value)

            if self._variable is not None and not from_variable_callback:
                self._variable_callback_blocked = True
                self._variable.set(value)
                self._variable_callback_blocked = False
        else:
            if self._current_value in self._buttons_dict:
                self._unselect_button_by_value(self._current_value)
            self._current_value = value

            if self._variable is not None and not from_variable_callback:
                self._variable_callback_blocked = True
                self._variable.set(value)
                self._variable_callback_blocked = False

        if from_button_callback:
            if self._command is not None:
                self._command(self._current_value)

    def get(self) -> str:
        return self._current_value

    def insert(self, index: int, value: str):
        if value not in self._buttons_dict:
            self._value_list.insert(index, value)
            self._buttons_dict[value] = self._create_button(index, value)

            self._configure_button_corners_for_index(index)
            if index > 0:
                self._configure_button_corners_for_index(index - 1)
            if index < len(self._buttons_dict) - 1:
                self._configure_button_corners_for_index(index + 1)

            self._create_button_grid()

            if value == self._current_value:
                self._select_button_by_value(self._current_value)
        else:
            raise ValueError(f"CTkSegmentedButton can not insert value '{value}', already part of the values")

    def delete(self, value: str):
        if value in self._buttons_dict:
            self._buttons_dict[value].destroy()
            self._buttons_dict.pop(value)
            index_to_remove = self._get_index_by_value(value)
            self._value_list.pop(index_to_remove)

            # removed index was outer right element
            if index_to_remove == len(self._buttons_dict) and len(self._buttons_dict) > 0:
                self._configure_button_corners_for_index(index_to_remove - 1)

            # removed index was outer left element
            if index_to_remove == 0 and len(self._buttons_dict) > 0:
                self._configure_button_corners_for_index(0)

            #if index_to_remove <= len(self._buttons_dict) - 1:
            #    self._configure_button_corners_for_index(index_to_remove)

            self._create_button_grid()
        else:
            raise ValueError(f"CTkSegmentedButton does not contain value '{value}'")
