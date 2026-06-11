function predictRisk()
{
    let risk = "Low Risk";

    localStorage.setItem("risk", risk);

    window.location.href = "result.html";
}