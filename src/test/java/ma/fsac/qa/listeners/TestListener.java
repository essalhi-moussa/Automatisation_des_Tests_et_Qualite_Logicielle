package ma.fsac.qa.listeners;

import io.qameta.allure.Allure;
import java.io.ByteArrayInputStream;
import ma.fsac.qa.base.BaseTest;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testng.ITestListener;
import org.testng.ITestResult;

/** Joint une capture d'ecran au rapport Allure lorsqu'un test UI echoue. */
public class TestListener implements ITestListener {

    private static final Logger LOG = LoggerFactory.getLogger(TestListener.class);

    @Override
    public void onTestStart(ITestResult result) {
        LOG.info("DEBUT  {}", result.getMethod().getMethodName());
    }

    @Override
    public void onTestSuccess(ITestResult result) {
        LOG.info("SUCCES {}", result.getMethod().getMethodName());
    }

    @Override
    public void onTestFailure(ITestResult result) {
        LOG.error("ECHEC  {} : {}", result.getMethod().getMethodName(), result.getThrowable().getMessage());
        WebDriver driver = BaseTest.getDriver();
        if (driver instanceof TakesScreenshot shooter) {
            try {
                byte[] png = shooter.getScreenshotAs(OutputType.BYTES);
                Allure.addAttachment("Capture d'ecran (echec)", "image/png", new ByteArrayInputStream(png), "png");
            } catch (RuntimeException e) {
                LOG.warn("Capture d'ecran impossible : {}", e.getMessage());
            }
        }
    }
}
