import flet as ft
import sqlite3
from pathlib import Path


#================== قاعدة البيانات


DB_PATH = Path(__file__).with_name("contacts.db")


def connecter_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            telephone TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


#================== البرنامج الرئيسي


def main(page: ft.Page):
    page.title = "إدارة جهات الاتصال"
    page.padding = 12
    page.spacing = 10
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F3F4F6"
    page.scroll = ft.ScrollMode.AUTO

    conn = connecter_db()
    contact_id = {"value": None}

    champ_nom = ft.TextField(
        label="الاسم الكامل",
        hint_text="أدخل الاسم",
        expand=True,
        border_radius=8,
    )

    champ_telephone = ft.TextField(
        label="رقم الهاتف",
        hint_text="أدخل رقم الهاتف",
        expand=True,
        border_radius=8,
        keyboard_type=ft.KeyboardType.PHONE,
    )

    champ_recherche = ft.TextField(
        label="بحث بالاسم أو الهاتف",
        hint_text="اكتب الاسم أو جزءًا منه أو رقم الهاتف",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=8,
    )

    message = ft.Text(size=13)

    tableau = ft.Column(
        spacing=3,
        scroll=ft.ScrollMode.AUTO,
    )

    #================== قراءة البيانات


    def lire_contacts():
        recherche = (champ_recherche.value or "").strip()

        if recherche:
            terme = f"%{recherche}%"
            return conn.execute(
                """
                SELECT id, nom, telephone
                FROM contacts
                WHERE nom LIKE ? OR telephone LIKE ?
                ORDER BY nom COLLATE NOCASE
                """,
                (terme, terme),
            ).fetchall()

        return conn.execute(
            """
            SELECT id, nom, telephone
            FROM contacts
            ORDER BY nom COLLATE NOCASE
            """
        ).fetchall()


    #================== إظهار الرسائل


    def afficher_message(texte, couleur="#006400"):
        message.value = texte
        message.color = couleur
        page.update()


    #================== اختيار جهة اتصال


    def selectionner_contact(row):
        contact_id["value"] = row[0]
        champ_nom.value = row[1]
        champ_telephone.value = row[2]

        actualiser_tableau()

        afficher_message(f"السجل المحدد: {row[1]}")


    #================== تحديث الجدول


    def actualiser_tableau():
        tableau.controls.clear()

        # عناوين الجدول
        tableau.controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                "الرقم",
                                color="#FFFFFF",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                            ),
                            expand=1,
                        ),
                        ft.Container(
                            content=ft.Text(
                                "الاسم",
                                color="#FFFFFF",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                            ),
                            expand=2,
                        ),
                        ft.Container(
                            content=ft.Text(
                                "الهاتف",
                                color="#FFFFFF",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                            ),
                            expand=2,
                        ),
                    ],
                ),
                bgcolor="#DA7297",
                padding=10,
                border_radius=5,
            )
        )

        # بيانات الجدول
        contacts = lire_contacts()

        for row in contacts:
            selectionne = contact_id["value"] == row[0]

            couleur_fond = "#3F2A1D" if selectionne else "#FFFFFF"
            couleur_texte = "#FFFFFF" if selectionne else "#222222"
            couleur_bordure = "#DA7297" if selectionne else "#D1D5DB"

            tableau.controls.append(
                ft.Container(
                    data=row[0],
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    str(row[0]),
                                    size=14,
                                    color=couleur_texte,
                                ),
                                expand=1,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    row[1],
                                    size=12,
                                    color=couleur_texte,
                                ),
                                expand=2,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    row[2],
                                    size=12,
                                    color=couleur_texte,
                                ),
                                expand=2,
                            ),
                        ],
                    ),
                    bgcolor=couleur_fond,
                    padding=10,
                    border=ft.Border.all(1, couleur_bordure),
                    border_radius=5,
                    on_click=lambda e, r=row: selectionner_contact(r),
                )
            )

        if not contacts:
            tableau.controls.append(
                ft.Container(
                    content=ft.Text(
                        "لا توجد بيانات لعرضها",
                        color="#666666",
                    ),
                    padding=15,
                    alignment=ft.Alignment.CENTER,
                )
            )

        page.update()


    #================== تفريغ الحقول


    def vider_champs(e=None):
        champ_nom.value = ""
        champ_telephone.value = ""
        contact_id["value"] = None

        message.value = ""

        actualiser_tableau()


    #================== إضافة جهة اتصال


    def ajouter_contact(e):
        nom = (champ_nom.value or "").strip()
        telephone = (champ_telephone.value or "").strip()

        if not nom or not telephone:
            afficher_message(
                "يرجى إدخال الاسم ورقم الهاتف.",
                "#B22222",
            )
            return

        conn.execute(
            "INSERT INTO contacts (nom, telephone) VALUES (?, ?)",
            (nom, telephone),
        )
        conn.commit()

        vider_champs()
        actualiser_tableau()

        afficher_message("تمت إضافة جهة الاتصال بنجاح.")


    #================== تعديل جهة اتصال


    def modifier_contact(e):
        identifiant = contact_id["value"]
        nom = (champ_nom.value or "").strip()
        telephone = (champ_telephone.value or "").strip()

        if identifiant is None:
            afficher_message(
                "اختر جهة اتصال من الجدول أولًا.",
                "#B22222",
            )
            return

        if not nom or not telephone:
            afficher_message(
                "يرجى إدخال الاسم ورقم الهاتف.",
                "#B22222",
            )
            return

        conn.execute(
            """
            UPDATE contacts
            SET nom = ?, telephone = ?
            WHERE id = ?
            """,
            (nom, telephone, identifiant),
        )
        conn.commit()

        vider_champs()
        actualiser_tableau()

        afficher_message("تم تعديل جهة الاتصال بنجاح.")


    #================== حذف جهة اتصال


    def supprimer_contact(e):
        identifiant = contact_id["value"]

        if identifiant is None:
            afficher_message(
                "اختر جهة اتصال من الجدول أولًا.",
                "#B22222",
            )
            return

        def confirmer(e):
            conn.execute(
                "DELETE FROM contacts WHERE id = ?",
                (identifiant,),
            )
            conn.commit()

            page.pop_dialog()
            vider_champs()
            actualiser_tableau()

            afficher_message("تم حذف جهة الاتصال بنجاح.")

        def annuler(e):
            page.pop_dialog()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("تأكيد الحذف"),
            content=ft.Text(
                "هل تريد حذف جهة الاتصال المحددة؟"
            ),
            actions=[
                ft.TextButton(
                    content="نعم",
                    on_click=confirmer,
                ),
                ft.TextButton(
                    content="لا",
                    on_click=annuler,
                ),
            ],
        )

        page.show_dialog(dialog)


    #================== البحث الفوري


    def rechercher(e):
        actualiser_tableau()


    champ_recherche.on_change = rechercher


    #================== الأزرار


    زر_اضافة = ft.Button(
        content="إضافة",
        icon=ft.Icons.ADD,
        on_click=اضافة if False else ajouter_contact,
        bgcolor="#006400",
        color="#FFFFFF",
        expand=True,
    )

    زر_تعديل = ft.Button(
        content="تعديل",
        icon=ft.Icons.EDIT,
        on_click=modifier_contact,
        bgcolor="#C45D7C",
        color="#FFFFFF",
        expand=True,
    )

    زر_حذف = ft.Button(
        content="حذف",
        icon=ft.Icons.DELETE,
        on_click=حذف if False else supprimer_contact,
        bgcolor="#B22222",
        color="#FFFFFF",
        expand=True,
    )

    زر_تفريغ = ft.Button(
        content="تفريغ",
        icon=ft.Icons.CLEAR,
        on_click=vider_champs,
        bgcolor="#555555",
        color="#FFFFFF",
        expand=True,
    )


    #================== بناء الواجهة


    page.add(
        ft.Text(
            "إدارة جهات الاتصال",
            size=24,
            weight=ft.FontWeight.BOLD,
            color="#3F2A1D",
        ),

        ft.Divider(color="#DA7297"),

        ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=champ_nom,
                    col={"xs": 12, "sm": 6},
                ),
                ft.Container(
                    content=champ_telephone,
                    col={"xs": 12, "sm": 6},
                ),
            ],
            spacing=8,
        ),

        ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=زر_اضافة,
                    col={"xs": 6, "sm": 3},
                ),
                ft.Container(
                    content=زر_تعديل,
                    col={"xs": 6, "sm": 3},
                ),
                ft.Container(
                    content=زر_حذف,
                    col={"xs": 6, "sm": 3},
                ),
                ft.Container(
                    content=زر_تفريغ,
                    col={"xs": 6, "sm": 3},
                ),
            ],
            spacing=8,
        ),

        message,

        champ_recherche,

        ft.Text(
            "جدول جهات الاتصال",
            size=17,
            weight=ft.FontWeight.BOLD,
            color="#3F2A1D",
        ),

        ft.Container(
            content=tableau,
            expand=True,
        ),
    )

    actualiser_tableau()


if __name__ == "__main__":
    ft.run(main)

