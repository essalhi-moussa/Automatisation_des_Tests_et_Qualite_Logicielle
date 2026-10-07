package ma.fsac.qa.tests.ui;

import static org.assertj.core.api.Assertions.assertThat;

import io.qameta.allure.Description;
import io.qameta.allure.Epic;
import io.qameta.allure.Feature;
import ma.fsac.qa.base.BaseTest;
import ma.fsac.qa.pages.FramesPage;
import ma.fsac.qa.pages.LocalFramesPage;
import ma.fsac.qa.utils.RetryAnalyzer;
import org.openqa.selenium.PageLoadStrategy;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

@Epic("Interface utilisateur")
@Feature("Frames imbriques (the-internet.herokuapp.com)")
public class FramesTests extends BaseTest {

    /** Avec la strategie EAGER, le chargement du frameset se bloque par moments : on utilise NONE et des attentes explicites. */
    @Override
    protected PageLoadStrategy pageLoadStrategy() {
        return PageLoadStrategy.NONE;
    }


    @DataProvider(name = "framesHaut")
    public Object[][] framesHaut() {
        return new Object[][] {{"left", "LEFT"}, {"middle", "MIDDLE"}, {"right", "RIGHT"}};
    }

    @Test(groups = "external", dataProvider = "framesHaut",
            retryAnalyzer = RetryAnalyzer.class,
            description = "UI-13 : lecture du contenu des frames imbriques (site externe)")
    @Description("Formy n a pas de page iFrame. L exigence est couverte sur the-internet.herokuapp.com/nested_frames. "
            + "La page /iframe (TinyMCE) a ete ecartee : editeur en lecture seule et chargement superieur a 30 s. "
            + "Groupe external : ce site tiers est instable (timeouts constates), il est donc execute a part (profil external).")
    public void lireFramesDuHaut(String position, String attendu) {
        FramesPage page = new FramesPage(getDriver()).open();
        assertThat(page.topFrameCount()).isEqualTo(3);
        assertThat(page.readTopFrame(position)).isEqualTo(attendu);
    }

    @Test(groups = "external", retryAnalyzer = RetryAnalyzer.class,
            description = "UI-14 : frame du bas puis retour au contenu principal (site externe)")
    public void lireFrameDuBas() {
        FramesPage page = new FramesPage(getDriver()).open();
        assertThat(page.readBottomFrame()).isEqualTo("BOTTOM");
        assertThat(page.readTopFrame("middle")).isEqualTo("MIDDLE");
    }

    @Test(groups = {"smoke", "ui"}, description = "UI-15 : iFrame et iFrame imbrique (page locale deterministe)")
    @Description("Meme exigence que UI-13 mais sur une page data: autonome, pour un resultat stable en CI.")
    public void lireIframesLocaux() {
        LocalFramesPage page = new LocalFramesPage(getDriver()).open();
        assertThat(page.readOuterFrame()).isEqualTo("Contenu externe");
        assertThat(page.readInnerFrame()).isEqualTo("Contenu imbrique");
        assertThat(page.parentTitle()).isEqualTo("Page parente");
    }
}
