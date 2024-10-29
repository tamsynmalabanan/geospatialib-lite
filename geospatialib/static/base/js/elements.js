const createDropdownMenuListItem = (label) => {
    const li = document.createElement('li')

    const button = document.createElement('button')
    button.className = 'dropdown-item'
    button.innerText = label

    li.appendChild(button)

    return li
}