package com.comp6239.Tutor;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.comp6239.Backend.Model.Student;
import com.comp6239.R;
import com.comp6239.Tutor.TutorStudentRequestsFragment.OnSearchStudentFragmentInteractionListener;

import java.util.List;

/**
 * {@link RecyclerView.Adapter} that can display a {@link Student} and makes a call to the
 * specified {@link OnSearchStudentFragmentInteractionListener}.
 * TODO: Replace the implementation with code for your data type.
 */
public class StudentRequestRecyclerViewAdapter extends RecyclerView.Adapter<StudentRequestRecyclerViewAdapter.ViewHolder> {

    private final List<Student> mValues;
    private final OnSearchStudentFragmentInteractionListener mListener;

    public StudentRequestRecyclerViewAdapter(List<Student> items, OnSearchStudentFragmentInteractionListener listener) {
        mValues = items;
        mListener = listener;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.fragment_student_requests, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(final ViewHolder holder, int position) {
        holder.mItem = mValues.get(position);
        holder.mIdView.setText(mValues.get(position).getFirstName());
        holder.mContentView.setText(mValues.get(position).getLastName());

        holder.mView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (null != mListener) {
                    // Notify the active callbacks interface (the activity, if the
                    // fragment is attached to one) that an item has been selected.
                    mListener.onSearchStudentFragmentInteraction(holder.mItem);
                }
            }
        });
    }

    @Override
    public int getItemCount() {
        return mValues.size();
    }

    public class ViewHolder extends RecyclerView.ViewHolder {
        public final View mView;
        public final TextView mIdView;
        public final TextView mContentView;
        public Student mItem;

        public ViewHolder(View view) {
            super(view);
            mView = view;
            mIdView = (TextView) view.findViewById(R.id.subject_name);
            mContentView = (TextView) view.findViewById(R.id.subject_number);
        }

        @Override
        public String toString() {
            return super.toString() + " '" + mContentView.getText() + "'";
        }
    }
}
