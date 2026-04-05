const SESSION_STORAGE_KEY = "pygame-dom-docs"

const sectionNav = document.querySelector(".section-nav")
const sectionHeaderText = document.querySelector("#section-header-text")
const sectionContent = document.querySelector(".content")
const scrollNav = document.querySelector("#scroll-nav")

let sessionData = {}

async function loadSectionData(sectionId, callback) {
    const result = await fetch(`pages/${sectionId}.json`)

    if (!result.ok) return

    const json = await result.json()

    if (!json) return

    callback(json)
}

function saveSessionData(data) {
    const jsonString = JSON.stringify(data)

    window.sessionStorage.setItem(SESSION_STORAGE_KEY, jsonString)
}

function loadSessionData() {
    const jsonString = window.sessionStorage.getItem(SESSION_STORAGE_KEY)

    if (!jsonString) return {}

    try {
        const data = JSON.parse(jsonString)

        return data
    }
    catch {
        console.warn("Could not load session data")
    }

    return null
}

function setupLinks() {
    const linkElements = sectionNav.querySelectorAll("p")

    for (const linkElement of linkElements) {
        linkElement.addEventListener("click", () => { window.location.href = `docs.html?section=${linkElement.getAttribute("section")}` })
    }
}

function loadSection(sectionData) {
    sectionHeaderText.textContent = sectionData.header

    for (const item of sectionData.content) {
        switch (item.type) {
            case "text":
                const textElement = document.createElement("p")
                textElement.innerHTML = item.text

                sectionContent.append(textElement)

                break
            case "text-margin":
                const textElementMargin = document.createElement("p")
                textElementMargin.innerHTML = item.text
                textElementMargin.style.marginBottom = "0.8vw"
                textElementMargin.style.marginTop = "0.8vw"

                sectionContent.append(textElementMargin)

                break
            case "subheader":
                const headerTextElement = document.createElement("h3")
                headerTextElement.innerHTML = item.text

                sectionContent.append(headerTextElement)

                break
            case "subsubheader":
                const headerSubTextElement = document.createElement("h4")
                headerSubTextElement.innerHTML = item.text

                sectionContent.append(headerSubTextElement)

                break
            case "code":
                const codeElement = document.createElement("div")
                codeElement.classList.add("code-block")

                const codeType = document.createElement("p")
                codeType.innerHTML = `${item.filename} <span>${item.lang}</span>`
                codeType.style.backgroundColor = item.header_color

                codeElement.append(codeType)

                for (const codeLine of item.code) {
                    const lineElement = document.createElement("h2")
                    lineElement.innerHTML = codeLine

                    codeElement.append(lineElement)
                }

                sectionContent.append(codeElement)

                break
        }
        
    }

    const footer = document.createElement("div")
    footer.classList.add("footer")

    sectionContent.append(footer)
}

function onWindowClose() {
    sessionData.leftNavScrollY = scrollNav.scrollTop

    saveSessionData(sessionData)
}

function main() {
    const urlParams = new URLSearchParams(window.location.search)

    let section = urlParams.get("section")

    if (!section) section = 0

    loadSectionData(section, loadSection)

    setupLinks()

    sessionData = loadSessionData()

    if (!sessionData || sessionData == {}) {
        sessionData = {
            "leftNavScrollY": 0
        }
    }

    scrollNav.scrollTop = sessionData.leftNavScrollY

    window.addEventListener("beforeunload", onWindowClose)
}

main()