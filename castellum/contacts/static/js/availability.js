'use strict';

const e = React.createElement;

const HOURS = [9, 10, 11, 12, 13, 14, 15, 16, 17];

class Checkbox extends React.Component {
    render() {
        return e('div', {className: 'form-check'}, [
            e('input', {key: 'input', className: 'form-check-input', type: 'checkbox'}),
            e('label', {key: 'label', className: 'form-check-label'}, this.props.children),
        ]);
    };
}

class FormGroup extends React.Component {
    render() {
        return e('div', {className: 'form-group'}, [
            e(Checkbox, {key: 'checkbox'}, this.props.children),
            e(
                'select',
                {key: 'select', className: 'form-control', multiple: {}},
                HOURS.map(hour => e('option', {key: hour, value: hour}, hour))
            ),
        ]);
    }
}

class Availability extends React.Component {
    render() {
        const weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

        return e(
            'div',
            {className: 'row', style: {width: '100%'}},
            weekdays.map(wd => e(
                'div',
                {key: wd, className: 'col-6 col-sm-2 mb-3'},
                e(FormGroup, {}, wd))
            )
        );
    }
}

const domContainer = document.querySelector('#availability');

ReactDOM.render(e(Availability), domContainer);
