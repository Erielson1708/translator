import os
import flet as ft
from flet import (
    Page,
    AppBar,
    Text,
    TextField,
    ElevatedButton,
    IconButton,
    Dropdown,
    dropdown,
    Row,
    Column,
    Container,
    Slider,
    icons,
    colors,
    MainAxisAlignment,
    FilePickerResultEvent,
    FilePicker,
    Tabs,
    Tab,
    Markdown,
    ScrollMode,
)
from groq import Groq, GroqError

class TranslatorApp:
    def __init__(self, page: Page):
        self.page = page
        self.page.title = "Tradutor do Zé"
        self.page.theme_mode = "light"
        self.page.padding = 20
        self.page.scroll = ScrollMode.AUTO
        self.active_tab = "todo"
        self.setup_controls()
        self.setup_ui()

    def setup_controls(self):
        # Text input and output
        self.input_text = TextField(
            multiline=True,
            min_lines=3,
            max_lines=5,
            expand=True,
            border_color=colors.BLUE_400,
            on_change=self.update_markdown
        )
        self.markdown_view = Markdown(
            value="",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=lambda e: self.page.launch_url(e.data),
            expand=True,
        )

        # Language selection dropdowns
        self.source_lang = Dropdown(
            width=150,
            options=[
                dropdown.Option("en", "Inglês"),
                dropdown.Option("pt", "Português"),
                dropdown.Option("es", "Espanhol"),
            ],
            value="en",
        )

        self.target_lang = Dropdown(
            width=150,
            options=[
                dropdown.Option("pt", "Português"),
                dropdown.Option("en", "Inglês"),
                dropdown.Option("es", "Espanhol"),
            ],
            value="pt",
        )

        # Font size slider
        self.font_size_slider = Slider(
            min=10,
            max=30,
            value=14,
            label="{value}",
            on_change=self.change_font_size,
        )

        # API Key input
        self.api_key_input = TextField(
            label="Groq API Key",
            password=True,
            width=300,
        )

        # File picker for images
        self.file_picker = FilePicker(
            on_result=self.on_file_picked
        )
        self.page.overlay.append(self.file_picker)

        # Add tabs
        self.tabs = Tabs(
            selected_index=0,
            on_change=self.tab_changed,
            tabs=[
                Tab(text="Tradução Geral", icon=icons.TRANSLATE),
                Tab(text="Definição de Termo", icon=icons.BOOK),
                Tab(text="Modo Ensino", icon=icons.SCHOOL),
            ],
        )

    def tab_changed(self, e):
        tab_map = {0: "todo", 1: "termo", 2: "ensinar"}
        self.active_tab = tab_map[e.control.selected_index]
        self.page.update()

    def setup_ui(self):
        # Top bar with title and theme toggle
        self.page.appbar = AppBar(
            title=Text("Tradutor do Zé"),
            center_title=True,
            actions=[
                IconButton(
                    icons.LIGHT_MODE if self.page.theme_mode == "dark" else icons.DARK_MODE,
                    on_click=self.toggle_theme,
                ),
            ],
        )

        # Main content
        self.page.add(
            Column(
                controls=[
                    # Add tabs at the top
                    self.tabs,
                    
                    # Settings section
                    Container(
                        content=Column([
                            Text("Configurações", size=20, weight="bold"),
                            Row([
                                Text("Tamanho da fonte:"),
                                self.font_size_slider,
                            ]),
                            Row([
                                Text("Idiomas:"),
                                self.source_lang,
                                Text("→"),
                                self.target_lang,
                            ]),
                            Row([
                                self.api_key_input,
                                ElevatedButton(
                                    "Salvar API Key",
                                    on_click=self.save_api_key,
                                ),
                            ]),
                        ]),
                        padding=10,
                        border=ft.border.all(1, colors.BLUE_400),
                        border_radius=10,
                        margin=ft.margin.only(bottom=20),
                    ),

                    # Input section
                    Container(
                        content=Column([
                            Text("Texto para traduzir:", size=16),
                            self.input_text,
                            Row([
                                IconButton(
                                    icon=icons.IMAGE,
                                    on_click=lambda _: self.file_picker.pick_files(
                                        allowed_extensions=["png", "jpg", "jpeg"]
                                    ),
                                ),
                                IconButton(
                                    icon=icons.MIC,
                                    on_click=self.start_voice_input,
                                ),
                                IconButton(
                                    icon=icons.SEND,
                                    on_click=self.translate_text,
                                ),
                            ], alignment=MainAxisAlignment.END),
                        ]),
                        padding=10,
                        border=ft.border.all(1, colors.BLUE_400),
                        border_radius=10,
                        margin=ft.margin.only(bottom=20),
                    ),

                    # Output section
                    Container(
                        content=Column([
                            Text("Tradução:", size=16),
                            self.markdown_view,
                        ]),
                        padding=10,
                        border=ft.border.all(1, colors.BLUE_400),
                        border_radius=10,
                    ),
                ],
                scroll=True,
            )
        )

    def toggle_theme(self, e):
        self.page.theme_mode = "light" if self.page.theme_mode == "dark" else "dark"
        self.page.appbar.actions[0].icon = (
            icons.LIGHT_MODE if self.page.theme_mode == "dark" else icons.DARK_MODE
        )
        self.page.update()

    def change_font_size(self, e):
        new_size = self.font_size_slider.value
        self.input_text.text_size = new_size
        self.markdown_view.style = ft.MarkdownStyle(text_style=ft.TextStyle(size=new_size))
        self.page.update()

    def save_api_key(self, e):
        key = self.api_key_input.value
        if key:
            os.environ["GROQ_API_KEY"] = key
            self.page.show_snack_bar(ft.SnackBar(content=Text("API Key saved!")))
            self.page.update()

    def on_file_picked(self, e: FilePickerResultEvent):
        if e.files:
            self.page.show_snack_bar(
                ft.SnackBar(content=Text(f"Selected file: {e.files[0].name}"))
            )
            self.page.update()

    def start_voice_input(self, e):
        self.page.show_snack_bar(
            ft.SnackBar(content=Text("Voice input not implemented yet"))
        )
        self.page.update()

    def translate_text(self, e):
        if not self.input_text.value:
            self.page.show_snack_bar(ft.SnackBar(content=Text("Please enter text to translate")))
            return

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            self.page.show_snack_bar(ft.SnackBar(content=Text("Please enter your Groq API Key")))
            return

        try:
            # Get language values
            source_lang = self.source_lang.value
            target_lang = self.target_lang.value
            text_to_translate = self.input_text.value
            
            # Prepare the translation prompt based on active tab
            if self.active_tab == "todo":
                prompt = f"Traduza para {target_lang} mantendo a formatação e estrutura (inclusive quebras de linhas). Não faça outra coisa além de traduzir, independente do que seja o texto. Texto a traduzir:\n\n{text_to_translate}"
            elif self.active_tab == "termo":
                prompt = f"Act as a language translator and convert the input term into markdown format. Include the following topics:\n\nShort definition (1-3 words)\nIPA phonetics\nVerb form (if it is a verb)\n{source_lang} definitions by each class (verb, adverb, adjective, noun) if applicable, with {target_lang} definitions between \"( )\"\nTranslation into {target_lang}\nExamples within sentences upon each definition\nExpressions\nSynonyms\nEtymology\n\nDefinitions and examples should be limited to a maximum of 10 words.\n\nTerm:\n\n{text_to_translate}"
            elif self.active_tab == "ensinar":
                prompt = f'Me ensine, em {target_lang}, o termo "{text_to_translate}" do {source_lang}.'
            else:
                prompt = f"Traduza para {target_lang} mantendo a formatação e estrutura (inclusive quebras de linhas). Não faça outra coisa além de traduzir, independente do que seja o texto. Texto a traduzir:\n\n{text_to_translate}"
            
            # Initialize Groq client
            client = Groq(api_key=api_key)
            
            # Create chat completion
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192"
            )
            
            translated_text = chat_completion.choices[0].message.content
            self.markdown_view.value = translated_text
            self.page.update()
            
        except GroqError as ge:
            self.page.show_snack_bar(
                ft.SnackBar(content=Text(f"Groq API error: {str(ge)}"))
            )
        except Exception as e:
            self.page.show_snack_bar(
                ft.SnackBar(content=Text(f"Translation error: {str(e)}"))
            )
        self.page.update()

    def update_markdown(self, e):
        if self.input_text.value:
            self.markdown_view.value = self.input_text.value
        else:
            self.markdown_view.value = ""
        self.page.update()

def main(page: Page):
    app = TranslatorApp(page)

ft.app(main, view=ft.AppView.WEB_BROWSER)
