package ma.fsac.qa.utils;

import org.testng.annotations.DataProvider;

/** Jeux de donnees centralises (TestNG data providers). */
public final class TestData {

    private TestData() {
    }

    /** prenom, nom, poste, niveau d'etudes (1-3), case sexe (1-3), experience, date. */
    @DataProvider(name = "inscriptionsValides")
    public static Object[][] inscriptionsValides() {
        return new Object[][] {
            {"Yassine", "Essalhi", "Ingenieur QA", 3, 1, "2-4", "10/05/2026"},
            {"Salma", "Benani", "Developpeuse Java", 2, 2, "0-1", "01/09/2025"},
            {"Omar", "El Idrissi", "Testeur logiciel", 1, 3, "10+", "15/12/2024"},
        };
    }

    /** libelle du menu, fragment d'URL attendu. */
    @DataProvider(name = "entreesMenu")
    public static Object[][] entreesMenu() {
        return new Object[][] {
            {"Buttons", "/buttons"},
            {"Checkbox", "/checkbox"},
            {"Radio Button", "/radiobutton"},
            {"Modal", "/modal"},
        };
    }

    /** libelle de l'option, valeur sous-jacente. */
    @DataProvider(name = "experiences")
    public static Object[][] experiences() {
        return new Object[][] {
            {"0-1"}, {"2-4"}, {"5-9"}, {"10+"},
        };
    }
}
