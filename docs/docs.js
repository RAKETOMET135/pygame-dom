const sectionNav = document.querySelector(".section-nav")
const sectionHeaderText = document.querySelector("#section-header-text")
const sectionContent = document.querySelector(".content")

async function loadSectionData(sectionId, callback) {
    const result = await fetch(`pages/${sectionId}.json`)

    if (!result.ok) return

    const json = await result.json()

    if (!json) return

    callback(json)
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
            case "subheader":
                const headerTextElement = document.createElement("h3")
                headerTextElement.innerHTML = item.text

                sectionContent.append(headerTextElement)

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
}

function main() {
    const urlParams = new URLSearchParams(window.location.search)

    let section = urlParams.get("section")

    if (!section) section = 0

    loadSectionData(section, loadSection)

    setupLinks()
}

main()